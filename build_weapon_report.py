"""
Combat equipment evaluation against a neutral reference dummy.

Produces, for every combat item, an effective-DPS figure that INCLUDES the
contribution of its special attacks -- so weapons are directly comparable
instead of requiring a manual read of each special.

Organised into tiers of 10 by equip requirement level.
Each item is evaluated three times: vs a melee, ranged, and magic dummy,
so the combat-triangle swing is visible per matchup.

=========================== MODEL & ASSUMPTIONS ===========================

REFERENCE PLAYER (per tier)
  All combat levels = tier midpoint (tier 30-39 -> level 35; top tier -> 115).
  No gear beyond the item under test. No prayers, potions, agility, auras.
  This isolates the item's own contribution.

REFERENCE DUMMY (per tier, scale-matched to the player)
  Defence level      = reference player level
  All defence bonuses= 0      -> evasion = (level + 9) * 64
  Damage reduction   = 0      -> weapon comparison is not muddied by DR
  Hitpoints level    = reference player level (HP = 10 x level), for kill time
  Attack type        = melee / ranged / magic (the three variants)

COMBAT TRIANGLE
  Damage multiplier applied per (player style, dummy style) using the
  Standard-mode table. Player style is inferred from the weapon.

DAMAGE ROLL TYPES HANDLED EXACTLY
  amplitude (Normal)      : % of the player's normal damage roll
  Custom / MaxHit         : maxPercent % of the player's max hit
  Custom / Fixed          : flat damage = maxPercent x 10
                            (verified: Malcs Razor-Sharp Claws maxPercent 52
                             -> 520 damage, matches wiki exactly)
  Custom / MaxHP (Target) : maxPercent % of dummy max HP
  Custom / CurrentHP      : maxPercent % of attacker HP (uses reference max HP)

DAMAGE ROLL TYPES FLAGGED, NOT SCORED
  MaxHitScaledByHP, MagicScaling, Bleeding, Poison*, Burn*, Cursed*,
  Reflection, DefenceLevel, Crystallize, HPUnder90, MaxHitDR, Surrounded,
  CurrentHPCapped200 -- these depend on fight state (target debuffed, HP
  thresholds, reflected damage) that a static dummy cannot represent.
  Items using them get `has_conditional_damage: true` and their scored DPS
  is a LOWER BOUND. Never treat those numbers as complete.

TURN STRUCTURE
  Each attack turn: roll specials by defaultChance. If the summed special
  chance exceeds 100, chances are normalised. Otherwise the remainder is a
  normal attack.
  Specials with `canNormalAttack: true` fire IN ADDITION to the normal
  attack rather than replacing it.
  Turn time = weapon attackSpeed. Multi-hit specials resolve within the turn
  (sub-hit interval x attackCount is almost always shorter than the weapon
  interval; where it is not, this model slightly overstates DPS).

ACCURACY
  hit chance from the verified two-part formula. `cantMiss` specials bypass
  it entirely -- which is why they rank far higher at low hit chance.

STATUS EFFECTS
  Self-buff effects (e.g. Warhorn) are converted to an uptime-weighted
  average modifier: uptime = 1 - (1 - chance)^turns.
  Damage-over-time and target debuffs are listed but not folded into DPS,
  since their value depends on fight length.
===========================================================================
"""
import json, os, math

BASE = '/home/claude/repo_test'
OUT = '/home/claude/index'
FILES = ['melvorDemo.json', 'melvorFull.json', 'melvorTotH.json', 'melvorExpansion2.json']

CT_DMG = {
    'melee':  {'melee': 1.00, 'ranged': 1.10, 'magic': 0.85},
    'ranged': {'melee': 0.85, 'ranged': 1.00, 'magic': 1.10},
    'magic':  {'melee': 1.10, 'ranged': 0.85, 'magic': 1.00},
}

CONDITIONAL_ROLLS = {
    'MaxHitScaledByHP', 'MaxHitScaledByHP2x', 'MagicScaling', 'Bleeding',
    'PoisonMax35', 'PoisonMin35', 'PoisonFixed100', 'PoisonedMaxHit',
    'BurnFixed100', 'BurnMaxHit100', 'CursedFixed100', 'Reflection',
    'DefenceLevel', 'Crystallize', 'HPUnder90', 'MaxHitDR',
    'CurrentHPCapped200', 'FixedPlusMaxHit50',
}


def accuracy_rating(level, bonus):
    return math.floor((level + 9) * (bonus + 64))


def evasion_rating(level, bonus):
    return math.floor((level + 9) * (bonus + 64))


def hit_chance(acc, eva):
    if acc < eva:
        return acc / (2 * eva)
    return 1 - eva / (2 * acc)


def melee_ranged_max_hit(level, strength_bonus):
    return math.floor(10 * (2.2 + level / 10 + (level + 17) * strength_bonus / 640))


def load():
    items, attacks, effects = {}, {}, {}
    for f in FILES:
        raw = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        ns, d = raw['namespace'], raw['data']
        for it in d.get('items', []):
            items[f'{ns}:{it["id"]}'] = {**it, '_ns': ns}
        for a in d.get('attacks', []):
            attacks[f'{ns}:{a["id"]}'] = a
        for e in d.get('combatEffects', []):
            effects[f'{ns}:{e["id"]}'] = e
    return items, attacks, effects


def item_tier(item):
    """Tier band from the highest combat-skill equip requirement."""
    lvl = 1
    for r in item.get('equipRequirements', []):
        if r.get('type') == 'SkillLevel':
            sk = r.get('skillID', '').split(':')[-1]
            if sk in ('Attack', 'Strength', 'Defence', 'Ranged', 'Magic',
                      'Hitpoints', 'Prayer', 'Slayer', 'Summoning'):
                lvl = max(lvl, r.get('level', 1))
    band = min((lvl - 1) // 10, 11)
    lo = band * 10 if band else 1
    hi = band * 10 + 9 if band < 11 else 120
    return band, lo, hi, lvl


def ref_level(band):
    return 115 if band == 11 else (band * 10 + 5 if band else 5)


def player_style(item):
    at = item.get('attackType')
    if at in ('melee', 'ranged', 'magic'):
        return at
    return 'melee'


def eval_special(a, effects, max_hit, avg_norm, hc, dummy_hp, ref_hp):
    """Return (expected damage per proc, cant_miss, conditional_flag, notes)."""
    conditional = False
    total = 0.0
    cant_miss = a.get('cantMiss', False)
    n_outer = a.get('attackCount', 1) or 1
    comps = a.get('damage', [])
    # An inner `attackCount` on a damage component is a HIT INDEX (0,1,2,3),
    # naming which of the outer hits that damage applies to -- NOT a multiplier.
    # e.g. Feather Storm: 4 components at 250/100/100/100% = four distinct hits.
    # When components carry no index, the single component describes every hit,
    # so it is multiplied by the outer attackCount instead.
    # e.g. Quad Swipe: one component at 100%, outer attackCount 4 -> 400%.
    per_hit_indexed = any('attackCount' in c for c in comps)
    for comp in comps:
        cnt = 1
        dtype = comp.get('damageType')
        if dtype == 'Normal':
            amp = comp.get('amplitude')
            if amp is None:
                conditional = True
                continue
            total += avg_norm * (amp / 100.0) * cnt
        else:
            roll = comp.get('maxRoll')
            pct = comp.get('maxPercent', 0)
            minpct = comp.get('minPercent')
            if roll in CONDITIONAL_ROLLS:
                conditional = True
                continue
            if roll == 'MaxHit':
                v = max_hit * (pct / 100.0)
            elif roll == 'Fixed':
                v = pct * 10.0
            elif roll == 'MaxHP':
                v = dummy_hp * (pct / 100.0)
            elif roll == 'CurrentHP':
                hi = ref_hp * (pct / 100.0)
                lo = ref_hp * ((minpct or pct) / 100.0)
                v = (hi + lo) / 2.0
            else:
                conditional = True
                continue
            if comp.get('roll') and minpct is not None and roll not in ('CurrentHP',):
                v = (v + v * (minpct / max(pct, 1e-9))) / 2.0
            total += v * cnt
    if not per_hit_indexed:
        total *= n_outer
    if not cant_miss:
        total *= hc
    return total, cant_miss, conditional


def self_buff_summary(a, effects):
    """Uptime-weighted self-buff modifiers from a special's prehit/onhit effects."""
    out = {}
    chance = (a.get('defaultChance') or 0) / 100.0
    for lst in ('prehitEffects', 'onhitEffects'):
        for ref in a.get(lst, []):
            eid = ref if isinstance(ref, str) else ref.get('effectID')
            e = effects.get(eid)
            if not e or e.get('target') != 'Self':
                continue
            turns = 1
            for p in e.get('parameters', []):
                if p.get('name') == 'turns':
                    turns = p.get('initialValue', 1)
            uptime = 1 - (1 - chance) ** max(turns, 1)
            for sg in e.get('statGroups', []):
                for k, v in sg.get('modifiers', {}).items():
                    if isinstance(v, (int, float)):
                        out[k] = round(out.get(k, 0) + v * uptime, 3)
    return out


def main():
    items, attacks, effects = load()
    results = []

    for iid, it in items.items():
        eqs = {e['key']: e['value'] for e in it.get('equipmentStats', [])}
        specials = it.get('specialAttacks', [])
        is_weapon = 'Weapon' in (it.get('validSlots') or [])
        if not is_weapon and not specials:
            continue
        if not it.get('validSlots'):
            continue

        band, lo, hi, req = item_tier(it)
        L = ref_level(band)
        style = player_style(it)
        spd = (eqs.get('attackSpeed') or 3000) / 1000.0

        if style == 'melee':
            atk_bonus = max(eqs.get('stabAttackBonus', 0), eqs.get('slashAttackBonus', 0),
                            eqs.get('blockAttackBonus', 0))
            str_bonus = eqs.get('meleeStrengthBonus', 0)
        elif style == 'ranged':
            atk_bonus = eqs.get('rangedAttackBonus', 0)
            str_bonus = eqs.get('rangedStrengthBonus', 0)
        else:
            atk_bonus = eqs.get('magicAttackBonus', 0)
            str_bonus = eqs.get('magicDamageBonus', 0)

        max_hit = melee_ranged_max_hit(L, str_bonus)
        min_hit = 1
        avg_norm = (max_hit + min_hit) / 2.0
        acc = accuracy_rating(L, atk_bonus)
        eva = evasion_rating(L, 0)
        hc = hit_chance(acc, eva)
        dummy_hp = L * 10
        ref_hp = L * 10

        sp_details, conditional_any = [], False
        chance_sum = sum((attacks[s].get('defaultChance') or 0)
                         for s in specials if s in attacks)
        norm_factor = 100.0 / chance_sum if chance_sum > 100 else 1.0

        for sref in specials:
            a = attacks.get(sref)
            if not a:
                continue
            ch = (a.get('defaultChance') or 0) * norm_factor / 100.0
            dmg, cant_miss, cond = eval_special(a, effects, max_hit, avg_norm,
                                                hc, dummy_hp, ref_hp)
            conditional_any = conditional_any or cond
            sp_details.append({
                'id': sref, 'name': a.get('name'), 'chance': round(ch * 100, 2),
                'cant_miss': cant_miss, 'attack_count': a.get('attack_count') or a.get('attackCount'),
                'expected_damage_per_proc': round(dmg, 1),
                'conditional': cond,
                'self_buffs': self_buff_summary(a, effects),
                'description': a.get('description'),
            })

        p_special = sum(s['chance'] for s in sp_details) / 100.0
        replaces = [s for s in sp_details
                    if not (attacks.get(s['id'], {}).get('canNormalAttack'))]
        additive = [s for s in sp_details
                    if attacks.get(s['id'], {}).get('canNormalAttack')]
        p_replace = sum(s['chance'] for s in replaces) / 100.0

        per_matchup = {}
        for dummy_style in ('melee', 'ranged', 'magic'):
            mult = CT_DMG[style][dummy_style]
            dmg_turn = (1 - p_replace) * avg_norm * hc
            for s in sp_details:
                dmg_turn += (s['chance'] / 100.0) * s['expected_damage_per_proc']
            dmg_turn *= mult
            dps = dmg_turn / spd
            per_matchup[dummy_style] = {
                'dps': round(dps, 2),
                'triangle_multiplier': mult,
                'kill_time_s': round(dummy_hp / dps, 1) if dps > 0 else None,
            }

        base_dps = avg_norm * hc / spd
        best = max(per_matchup.values(), key=lambda x: x['dps'])['dps']
        results.append({
            'id': iid, 'name': it.get('name'), 'namespace': it.get('_ns'),
            'tier_band': band, 'tier_label': f'{lo}-{hi}', 'equip_level': req,
            'player_style': style, 'slot': it.get('validSlots'),
            'two_handed': 'Shield' in (it.get('occupiesSlots') or []),
            'reference_level': L,
            'attack_speed_s': spd,
            'attack_bonus': atk_bonus, 'strength_bonus': str_bonus,
            'damage_reduction': eqs.get('damageReduction', 0),
            'max_hit_vs_dummy': max_hit,
            'accuracy_rating': acc, 'dummy_evasion': eva,
            'hit_chance_pct': round(hc * 100, 1),
            'dps_no_specials': round(base_dps, 2),
            'dps_by_dummy': per_matchup,
            # Share of best-matchup DPS coming from specials. Undefined when the
            # weapon's normal attack is non-viable (negative accuracy joke items),
            # so it is reported as None rather than a misleading >100% figure.
            'special_share_pct': (round(max(0.0, 1 - base_dps / best) * 100, 1)
                                  if specials and best > 0 and base_dps > 0
                                  else (None if specials else 0.0)),
            'specials': sp_details,
            'has_conditional_damage': conditional_any,
            'equipRequirements': it.get('equipRequirements', []),
        })

    results.sort(key=lambda r: (r['tier_band'], -max(
        m['dps'] for m in r['dps_by_dummy'].values())))

    out = {
        'model': 'neutral reference dummy, scale-matched per tier; no gear, '
                 'prayers, potions or agility beyond the item under test',
        'tiers': 'bands of 10 by highest combat-skill equip requirement',
        'count': len(results),
        'items': results,
    }
    with open(os.path.join(OUT, 'weapon_report.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    n_sp = sum(1 for r in results if r['specials'])
    n_cond = sum(1 for r in results if r['has_conditional_damage'])
    n_cm = sum(1 for r in results
               if any(s['cant_miss'] for s in r['specials']))
    print(f'Items evaluated              : {len(results)}')
    print(f'  carrying special attacks   : {n_sp}')
    print(f'  with cantMiss specials     : {n_cm}')
    print(f'  with conditional damage    : {n_cond}  (scored DPS = lower bound)')
    import collections
    band_counts = collections.Counter(r['tier_label'] for r in results)
    print('\nItems per tier:')
    for lab in sorted(band_counts, key=lambda x: int(x.split('-')[0])):
        print(f'  {lab:<8} {band_counts[lab]}')


if __name__ == '__main__':
    main()

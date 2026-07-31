"""
Build the combat item layer: weapons/armour with equipment stats, resolved
special attacks (damage components + linked status effects), and sources.
Reuses source resolution from item_index.json.
"""
import json, os

BASE = '/home/claude/repo_test'
OUT = '/home/claude/index'
FILES = ['melvorDemo.json', 'melvorFull.json', 'melvorTotH.json', 'melvorExpansion2.json']

def main():
    items = {}
    attacks = {}
    effects = {}
    effect_groups = {}

    for f in FILES:
        raw = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        ns = raw['namespace']
        d = raw['data']
        for it in d.get('items', []):
            full = f'{ns}:{it["id"]}'
            it2 = dict(it); it2['_namespace'] = ns
            items[full] = it2
        for a in d.get('attacks', []):
            full = f'{ns}:{a["id"]}'
            attacks[full] = {**a, '_namespace': ns}
        for e in d.get('combatEffects', []):
            full = f'{ns}:{e["id"]}'
            effects[full] = {**e, '_namespace': ns}
        for g in d.get('combatEffectGroups', []):
            full = f'{ns}:{g["id"]}'
            effect_groups[full] = g

    # load existing item_index for source lookup
    prior = json.load(open(os.path.join(OUT, 'item_index.json'), encoding='utf-8'))
    src_by_id = {e['id']: e['sources'] for e in prior['items']}

    def resolve_effect(eff_ref):
        eid = eff_ref if isinstance(eff_ref, str) else eff_ref.get('effectID')
        e = effects.get(eid)
        if not e:
            return {'id': eid, 'unresolved': True}
        dmg_groups = e.get('damageGroups', [])
        duration = None
        for p in e.get('parameters', []):
            if p.get('name') == 'turns':
                duration = p.get('initialValue')
        interval_mod = None
        for sg in e.get('statGroups', []):
            if 'attackInterval' in sg.get('modifiers', {}):
                interval_mod = sg['modifiers']['attackInterval']
        return {
            'id': eid,
            'name': e.get('name'),
            'duration_turns': duration,
            'damage_groups': dmg_groups,
            'attack_interval_modifier': interval_mod,
            'effect_groups': e.get('effectGroups', []),
        }

    def resolve_attack(attack_id):
        a = attacks.get(attack_id)
        if not a:
            return {'id': attack_id, 'unresolved': True}
        return {
            'id': attack_id,
            'name': a.get('name'),
            'default_chance_pct': a.get('defaultChance'),
            'damage_components': a.get('damage', []),  # each: damageType, amplitude(%), attackCount position
            'attack_count': a.get('attackCount'),
            'sub_hit_interval_ms': a.get('attackInterval'),
            'cant_miss': a.get('cantMiss', False),
            'lifesteal_pct': a.get('lifesteal', 0),
            'uses_runes_per_proc': a.get('usesRunesPerProc', False),
            'restricted_attack_types': a.get('attackTypes'),
            'onhit_effects': [resolve_effect(e) for e in a.get('onhitEffects', [])],
            'prehit_effects': [resolve_effect(e) for e in a.get('prehitEffects', [])],
            'description': a.get('description'),
        }

    combat_items = []
    for iid, it in items.items():
        eqstats_list = it.get('equipmentStats', [])
        if not eqstats_list and not it.get('specialAttacks'):
            continue
        if not it.get('validSlots'):
            continue
        eqstats = {e['key']: e['value'] for e in eqstats_list}
        special_attacks = [resolve_attack(a) for a in it.get('specialAttacks', [])]
        combat_items.append({
            'id': iid,
            'name': it.get('name'),
            'namespace': it.get('_namespace'),
            'tier': it.get('tier'),
            'type': it.get('type'),
            'attackType': it.get('attackType'),
            'ammoTypeRequired': it.get('ammoTypeRequired'),
            'validSlots': it.get('validSlots'),
            'occupiesSlots': it.get('occupiesSlots', []),
            'equipRequirements': it.get('equipRequirements', []),
            'equipmentStats': eqstats,
            'modifiers': it.get('modifiers', {}),
            'specialAttacks': special_attacks,
            'sources': src_by_id.get(iid, []),
        })

    with open(os.path.join(OUT, 'combat_item_index.json'), 'w', encoding='utf-8') as fh:
        json.dump({'count': len(combat_items), 'items': combat_items}, fh, indent=1, ensure_ascii=False)

    with open(os.path.join(OUT, 'combat_effects_index.json'), 'w', encoding='utf-8') as fh:
        resolved_effects = {eid: resolve_effect(eid) for eid in effects}
        json.dump({'count': len(resolved_effects), 'effects': resolved_effects}, fh, indent=1, ensure_ascii=False)

    n_special = sum(1 for it in combat_items if it['specialAttacks'])
    n_src = sum(1 for it in combat_items if it['sources'])
    print(f'Combat items (weapon/armour/jewellery with stats): {len(combat_items)}')
    print(f'  carrying at least one special attack: {n_special}')
    print(f'  with a resolved source               : {n_src}')
    print(f'Distinct special attacks resolved: {len(attacks)}')
    print(f'Distinct status effects resolved : {len(effects)}')

if __name__ == '__main__':
    main()

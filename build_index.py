"""
Build a unified item + source index for the Melvor progression project.
Reads game data (melvorDemo/Full/TotH/Expansion2) + wiki dump.
Outputs: item_index.json — one entry per item, with modifiers, requirements,
equip slots, and every source (monster, dungeon, thieving NPC, shop) that
can produce it.
"""
import json, os

BASE = '/home/claude/repo_test'
OUT = '/home/claude/index'

FILES = ['melvorDemo.json', 'melvorFull.json', 'melvorTotH.json', 'melvorExpansion2.json']

def load_all():
    data = {}
    for f in FILES:
        d = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        data[d['data'].get('namespace', f)] = d['data']
        data[f] = d['data']
    return data

def main():
    items = {}          # full_id -> item dict (+ 'namespace')
    monsters = {}        # full_id -> monster dict
    dungeons = {}
    strongholds = {}
    thieving_npcs = {}
    shop_purchases = {}
    agility_obstacles = {}
    agility_pillars = {}

    for f in FILES:
        raw = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        ns = raw['namespace']
        d = raw['data']
        for it in d.get('items', []):
            full = f'{ns}:{it["id"]}'
            it2 = dict(it); it2['_namespace'] = ns
            items[full] = it2
        for m in d.get('monsters', []):
            full = f'{ns}:{m["id"]}'
            monsters[full] = {'name': m['name'], 'namespace': ns, 'lootTable': m.get('lootTable', [])}
        for dg in d.get('dungeons', []):
            full = f'{ns}:{dg["id"]}'
            dungeons[full] = {'name': dg['name'], 'namespace': ns, 'rewards': dg.get('rewards', [])}
        for sh in d.get('strongholds', []):
            full = f'{ns}:{sh.get("id","?")}'
            strongholds[full] = sh
        for sp in d.get('shopPurchases', []):
            full = f'{ns}:{sp["id"]}'
            shop_purchases[full] = {'namespace': ns, **sp}
        for sd in d.get('skillData', []):
            sid = sd['skillID'].split(':')[-1]
            if sid == 'Thieving':
                for npc in sd['data'].get('npcs', []):
                    full = f'{ns}:{npc["id"]}'
                    thieving_npcs[full] = {'name': npc['name'], 'namespace': ns, 'uniqueDrop': npc.get('uniqueDrop'), 'lootTable': npc.get('lootTable', [])}
            if sid == 'Agility':
                for o in sd['data'].get('obstacles', []):
                    full = f'{ns}:{o["id"]}'
                    agility_obstacles[full] = {**o, '_namespace': ns}
                for p in sd['data'].get('pillars', []):
                    full = f'{ns}:{p["id"]}'
                    agility_pillars[full] = {**p, '_namespace': ns}

    # --- Build reverse source map: item_full_id -> [source dicts] ---
    sources = {}
    def add_source(item_id, src):
        sources.setdefault(item_id, []).append(src)

    for mid, m in monsters.items():
        for l in m['lootTable']:
            add_source(l['itemID'], {'type': 'monster', 'name': m['name'], 'id': mid})

    for did, dg in dungeons.items():
        for r in dg['rewards']:
            rid = r if isinstance(r, str) else r.get('itemID')
            if rid:
                add_source(rid, {'type': 'dungeon', 'name': dg['name'], 'id': did})

    for nid, npc in thieving_npcs.items():
        if npc['uniqueDrop']:
            add_source(npc['uniqueDrop']['id'], {'type': 'thieving', 'name': npc['name'], 'id': nid})
        for l in npc['lootTable']:
            add_source(l['itemID'], {'type': 'thieving_common', 'name': npc['name'], 'id': nid})

    for spid, sp in shop_purchases.items():
        for it in sp.get('contains', {}).get('items', []):
            iid = it if isinstance(it, str) else it.get('id')
            if iid:
                add_source(iid, {'type': 'shop', 'name': sp.get('customName') or sp['id'], 'id': spid})

    for f in FILES:
        raw = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        ns = raw['namespace']
        d = raw['data']
        for sd in d.get('skillData', []):
            sid = sd['skillID'].split(':')[-1]
            for r in sd['data'].get('recipes', []):
                pid = r.get('productID')
                if pid:
                    add_source(pid, {'type': 'craft', 'skill': sid, 'name': r.get('name') or r.get('id'), 'level': r.get('level')})

    # --- Classify modifier keys ---
    NONCOMBAT_PREFIXES = ['skillInterval', 'flatSkillInterval', 'skillXP', 'nonCombatSkillXP',
                           'masteryXP', 'skillPreservationChance', 'skillItemDoublingChance',
                           'globalItemDoublingChance', 'basePrimaryProductQuantity',
                           'flatBasePrimaryProductQuantity', 'currencyGain', 'flatCurrencyGain']
    COMBAT_STAT_KEYS = ['meleeAttackBonus', 'stabAttackBonus', 'slashAttackBonus', 'blockAttackBonus',
                         'rangedAttackBonus', 'magicAttackBonus', 'meleeStrengthBonus',
                         'rangedStrengthBonus', 'magicDamageBonus', 'meleeDefenceBonus',
                         'rangedDefenceBonus', 'magicDefenceBonus', 'damageReduction', 'attackSpeed']

    entries = []
    for iid, it in items.items():
        mods = it.get('modifiers') or {}
        eqstats = {e['key']: e['value'] for e in it.get('equipmentStats', [])} if it.get('equipmentStats') else {}
        has_nc = any(any(k.startswith(p) for p in NONCOMBAT_PREFIXES) for k in mods)
        has_combat = bool(set(eqstats) & set(COMBAT_STAT_KEYS)) or bool(it.get('validSlots')) and it.get('type') and 'Weapon' in str(it.get('type'))
        if not (mods or eqstats):
            continue  # skip pure materials/resources with no modifiers at all
        entries.append({
            'id': iid,
            'name': it.get('name'),
            'namespace': it.get('_namespace'),
            'validSlots': it.get('validSlots', []),
            'occupiesSlots': it.get('occupiesSlots', []),
            'equipRequirements': it.get('equipRequirements', []),
            'equipmentStats': eqstats,
            'modifiers': mods,
            'is_noncombat_modifier': has_nc,
            'is_combat_item': has_combat,
            'sources': sources.get(iid, []),
        })

    with open(os.path.join(OUT, 'item_index.json'), 'w', encoding='utf-8') as fh:
        json.dump({'count': len(entries), 'items': entries}, fh, indent=1, ensure_ascii=False)

    # summary
    nc = sum(1 for e in entries if e['is_noncombat_modifier'])
    cb = sum(1 for e in entries if e['is_combat_item'])
    with_src = sum(1 for e in entries if e['sources'])
    print(f'Total modifier-bearing items: {len(entries)}')
    print(f'  non-combat-modifier items : {nc}')
    print(f'  combat items               : {cb}')
    print(f'  with a resolved source     : {with_src}')
    print(f'  no resolved source (craft/shop-direct/other): {len(entries)-with_src}')

if __name__ == '__main__':
    main()

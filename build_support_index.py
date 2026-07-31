"""
Build the linked tables for slot-competing non-item bonuses: Agility
obstacles/pillars, Astrology constellations/stars, Summoning synergies.
These aren't items, but they occupy exclusive slots the same way equipment
does, so the roadmap and applet need them in the same queryable form.
"""
import json, os

BASE = '/home/claude/repo_test'
OUT = '/home/claude/index'
FILES = ['melvorDemo.json', 'melvorFull.json', 'melvorTotH.json', 'melvorExpansion2.json']

def main():
    agility_obstacles = []
    agility_pillars = []
    astrology = []
    summoning_synergies = []
    summoning_recipes = {}

    for f in FILES:
        raw = json.load(open(os.path.join(BASE, f), encoding='utf-8'))
        ns = raw['namespace']
        d = raw['data']
        for sd in d.get('skillData', []):
            sid = sd['skillID'].split(':')[-1]
            sdata = sd['data']
            if sid == 'Agility':
                for o in sdata.get('obstacles', []):
                    agility_obstacles.append({
                        'id': f'{ns}:{o["id"]}', 'name': o.get('name'), 'namespace': ns,
                        'slot_category': o.get('category'), 'base_interval_ms': o.get('baseInterval'),
                        'base_xp': o.get('baseExperience'), 'skill_requirements': o.get('skillRequirements', []),
                        'item_costs': o.get('itemCosts', []), 'gp_cost': next((c['quantity'] for c in o.get('currencyCosts', []) if c['id']=='melvorD:GP'), None),
                        'modifiers': o.get('modifiers', {}),
                    })
                for p in sdata.get('pillars', []):
                    agility_pillars.append({
                        'id': f'{ns}:{p["id"]}', 'name': p.get('name'), 'namespace': ns,
                        'modifiers': p.get('modifiers', {}),
                        'item_costs': p.get('itemCosts', []),
                    })
            if sid == 'Astrology':
                for c in sdata.get('recipes', []):
                    def flatten_tier(tier_list, cumulative_note):
                        out = []
                        for star in tier_list:
                            out.append({
                                'modifiers': star.get('modifiers', {}),
                                'max_count': star.get('maxCount'),
                                'costs_per_level': star.get('costs', []),
                                'total_cost_to_max': sum(star.get('costs', [])),
                                'unlock_requirements': star.get('unlockRequirements', []),
                            })
                        return out
                    astrology.append({
                        'id': f'{ns}:{c["id"]}', 'name': c.get('name'), 'namespace': ns,
                        'level_required': c.get('level'), 'linked_skills': c.get('skillIDs', []),
                        'standard_stars': flatten_tier(c.get('standardModifiers', []), 'stardust'),
                        'unique_stars': flatten_tier(c.get('uniqueModifiers', []), 'golden_stardust'),
                    })
            if sid == 'Summoning':
                for r in sdata.get('recipes', []):
                    summoning_recipes[f'{ns}:{r["id"]}'] = r
                for syn in sdata.get('synergies', []):
                    summoning_synergies.append({
                        'namespace': ns,
                        'summon_ids': syn.get('summonIDs', []),
                        'modifiers': syn.get('modifiers', {}),
                        'consumes_on': syn.get('consumesOn', []),
                    })

    out = {
        'agility_obstacles': {'count': len(agility_obstacles), 'items': agility_obstacles},
        'agility_pillars': {'count': len(agility_pillars), 'items': agility_pillars},
        'astrology_constellations': {'count': len(astrology), 'items': astrology},
        'summoning_synergies': {'count': len(summoning_synergies), 'items': summoning_synergies},
    }
    with open(os.path.join(OUT, 'support_index.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)

    print(f'Agility obstacles     : {len(agility_obstacles)}')
    print(f'Agility pillars       : {len(agility_pillars)}')
    print(f'Astrology constellations: {len(astrology)}')
    total_stars = sum(len(c['standard_stars']) + len(c['unique_stars']) for c in astrology)
    print(f'  total stars across all: {total_stars}')
    print(f'Summoning synergies   : {len(summoning_synergies)}')

if __name__ == '__main__':
    main()

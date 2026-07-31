# item_index.json

Unified item + source index built from the four game data files.
1,705 items carrying at least one modifier or combat stat, each tagged with
every source (monster kill, dungeon reward, Thieving unique, shop purchase,
or crafting recipe) that can produce it.

## Structure
```json
{
  "count": 1705,
  "items": [
    {
      "id": "melvorF:Gold_Topaz_Ring",
      "name": "Gold Topaz Ring",
      "namespace": "melvorF",
      "validSlots": ["Ring"],
      "occupiesSlots": [],
      "equipRequirements": [...],
      "equipmentStats": {...},
      "modifiers": {...},
      "is_noncombat_modifier": true,
      "is_combat_item": false,
      "sources": [
        {"type": "monster", "name": "...", "id": "..."},
        {"type": "thieving_common", "name": "...", "id": "..."},
        {"type": "craft", "skill": "Crafting", "name": "...", "level": 40}
      ]
    }
  ]
}
```

`sources[].type` is one of: `monster`, `dungeon`, `thieving` (NPC unique drop),
`thieving_common` (NPC regular loot table), `shop`, `craft` (artisan recipe
across Smithing/Fletching/Crafting/Runecrafting/Herblore/Cooking/Summoning).

## Coverage
- 774 / 1705 items (45%) have at least one resolved source.
- Remaining ~931 are mostly: quest/event-specific rewards, Township task
  rewards, and starting/untracked-source items — not yet cross-referenced.
  Township task reward resolution is the next planned addition.

## Regenerating
Run `python3 build_index.py` from a directory containing the four game data
JSON files (melvorDemo/Full/TotH/Expansion2).

# combat_item_index.json / combat_effects_index.json

The combat-side counterpart to item_index.json. Every weapon/armour/jewellery
item with equipment stats, joined to its special attack(s) — each special
attack fully resolved into damage components, sub-hit timing, trigger chance,
and any status effect it applies.

## combat_item_index.json
1,201 items with equipment stats. 186 carry at least one special attack.
611 have a resolved source (see item_index.json's source types).

Special attacks are embedded inline (not just referenced by ID) so a combat
sim can read one item entry and have everything needed to compute its DPS
contribution without a second lookup.

## combat_effects_index.json
All 230 status effects (Frostburn, Stun, Poison, etc.), each with:
- `duration_turns`
- `damage_groups` — the effect's own damage-over-time formula, if any
- `attack_interval_modifier` — e.g. Frostburn's +10% interval per stack
- `effect_groups` — tags like Debuff/Buff/Frostburn used for stacking rules

## Verified example
Infernal Claw -> Quad Swipe: 15% trigger chance, 4 consecutive hits at 100%
amplitude each, 300ms apart. Matches the wiki's dungeon-guide description of
the weapon exactly, now in a form the combat model can consume directly.

## Regenerating
Run after item_index.json exists (it reuses that file's source resolution):
`python3 build_combat_index.py`

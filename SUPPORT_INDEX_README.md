# support_index.json

Linked tables for the non-item bonuses that compete for exclusive slots the
same way equipment does: Agility obstacles/pillars, Astrology constellations
(with every star's per-level cost and unlock requirement), and Summoning
synergies.

## Contents
- **agility_obstacles** (79): slot category, requirements, item/GP cost, modifiers
- **agility_pillars** (6): the 3 base + 3 Elite (TotH) pillars, full modifier lists
- **astrology_constellations** (16): each with `standard_stars` (cost in
  Stardust, capped at 8 upgrades) and `unique_stars` (cost in Golden
  Stardust, capped at 5), each star carrying its per-level cost array and
  `total_cost_to_max`
- **summoning_synergies** (206): both familiar IDs, the bonus modifiers, and
  what the synergy consumes on

## Verified
Deedree constellation's first standard star sums to exactly 2,550 Stardust
to max — matches the wiki's stated figure, computed independently from the
raw per-level cost array rather than copied.

## Regenerating
`python3 build_support_index.py`

---

This completes the index: item_index.json (non-combat), combat_item_index.json
+ combat_effects_index.json (combat), and support_index.json (this file) —
four files covering every modifier-bearing thing in the game plus its source
and its competitors for the same slot.

# Combat Equipment Report — Neutral Dummy Framework

Effective DPS **including special attacks**, against a neutral reference dummy
scale-matched to each tier. Three columns per item for the combat-triangle
matchup vs a melee, ranged, and magic dummy.

## Model

- **Reference player:** all combat levels at tier midpoint. No gear, prayers,
  potions, agility, or auras beyond the item under test — this isolates the
  item's own contribution.
- **Dummy:** Defence level = player level, all defence bonuses 0, damage
  reduction 0, HP = 10 x level. Evasion = (level + 9) x 64.
- **Turn:** specials roll by trigger chance; the remainder is a normal attack.
  Specials flagged  fire in addition rather than replacing.
- **Damage rolls handled exactly:** amplitude, MaxHit %, Fixed (= maxPercent x 10,
  verified against Malcs Razor-Sharp Claws = 520), MaxHP %, CurrentHP %.

## Column key

- **spec%** — share of the item's best-matchup DPS coming from its special.
  High values mean raw stat comparison badly understates the weapon.
   = the normal attack is non-viable (joke items with negative accuracy).
- **CM** — carries a  special. Bypasses accuracy entirely, so these
  rank far higher than shown whenever your hit chance against a real target is poor.
- **!** — special uses conditional damage (target debuffed, HP thresholds,
  reflection). **Scored DPS is a lower bound** for these items.
- **2H** — occupies the shield slot.

---

## Tier 1-9 — reference level 5

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| DEBUG Stick | melee | 0.05s | 100.0% | 343919.98 | 378311.98 | 292331.98 | 0.0% |  |
| Candy Cane | melee | 10.0s | -7762.5% | 34848.45 | 38333.29 | 29621.18 | n/a | CM 2H |
| Sword of Some Reliability | melee | 2.4s | 75.6% | 9.64 | 10.6 | 8.19 | 27.2% |  |
| Throwing Dragon Sword | ranged | 2.4s | 75.6% | 6.56 | 7.71 | 8.49 | 0.0% |  |
| Almighty Lute | melee | 3.6s | 75.9% | 7.49 | 8.24 | 6.37 | 0.0% | 2H |
| Tilted Crossbow | ranged | 3.2s | 73.3% | 4.49 | 5.28 | 5.81 | 9.3% |  |
| Oak Longbow | ranged | 3.0s | 60.0% | 3.82 | 4.5 | 4.95 | 0.0% | 2H |
| Frostburn Wand | magic | 2.6s | 66.7% | 4.79 | 3.7 | 4.36 | 9.0% |  |
| Black 2H Sword | melee | 3.6s | 69.8% | 4.17 | 4.59 | 3.54 | 0.0% | 2H |
| Black Scimitar | melee | 2.4s | 61.4% | 4.1 | 4.51 | 3.48 | 0.0% |  |
| Steel Crossbow | ranged | 3.2s | 65.2% | 3.46 | 4.08 | 4.48 | 0.0% |  |
| Black Sword | melee | 2.4s | 61.0% | 4.07 | 4.47 | 3.46 | 0.0% |  |
| Sacrificial Dagger | melee | 2.4s | 61.0% | 4.07 | 4.47 | 3.46 | 0.0% |  |
| Black Dagger | melee | 2.2s | 59.5% | 4.06 | 4.46 | 3.45 | 0.0% |  |
| Steel Sword | melee | 2.4s | 60.0% | 4.0 | 4.4 | 3.4 | 0.0% |  |
| Steel Dagger | melee | 2.2s | 58.4% | 3.98 | 4.38 | 3.39 | 0.0% |  |

**Non-weapon items granting special attacks:**

- **Ring of Spirit Power** (Ring) — Spirit Power, 100.0% chance
- **Enchanted Topaz Bolts** (Quiver) — Topaz Shots, 30.0% chance
- **Topaz Bolts (Enchanted)** (Quiver) — Topaz Shots, 30.0% chance
- **Topaz Bolts (Arcane)** (Quiver) — Topaz Shots, 30.0% chance
- **Mage Mask** (Helmet) — Burning Roots, 30.0% chance
- **Shatter Arrows** (Quiver) — Shatter Arrow, 50.0% chance
- **Ring of Blade Echoes** (Ring) — Blade Echoes, 100.0% chance
- **Palladium Zephyte Necklace** (Amulet) — Reduction, 20.0% chance *(cantMiss)*
- **Enchanted Sapphire Bolts** (Quiver) — Sapphire Shots, 30.0% chance
- **Enchanted Ruby Bolts** (Quiver) — Ruby Shots, 30.0% chance

## Tier 10-19 — reference level 15

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Crystal 2H Hammer | melee | 3.6s | 71.4% | 9.55 | 10.5 | 8.11 | 38.6% | 2H |
| Crystal Twin Blades | melee | 2.2s | 61.9% | 8.59 | 9.45 | 7.3 | 30.0% | 2H |
| Old Hunting Bow | ranged | 3.0s | 64.0% | 7.08 | 8.33 | 9.16 | 19.6% | CM 2H |
| Crystal Crossbow | ranged | 3.2s | 67.3% | 6.25 | 7.35 | 8.09 | 22.0% |  |
| Willow Longbow | ranged | 3.0s | 63.6% | 6.13 | 7.21 | 7.93 | 0.0% | 2H |
| Crystal Longbow | ranged | 3.0s | 63.6% | 6.13 | 7.21 | 7.93 | 0.0% | 2H |
| Aranite 2H Blade | melee | 3.6s | 71.9% | 6.79 | 7.47 | 5.77 | 0.0% | 2H |
| Mithril 2H Sword | melee | 3.6s | 70.6% | 6.38 | 7.02 | 5.42 | 0.0% | 2H |
| Mithril Crossbow | ranged | 3.2s | 67.3% | 5.37 | 6.31 | 6.95 | 0.0% |  |
| Mithril Scimitar | melee | 2.4s | 62.4% | 6.24 | 6.86 | 5.3 | 0.0% |  |
| Willow Shortbow | ranged | 2.6s | 60.0% | 5.2 | 6.12 | 6.73 | 0.0% | 2H |
| Crystal Shortbow | ranged | 2.6s | 60.0% | 5.2 | 6.12 | 6.73 | 0.0% | 2H |
| Mithril Dagger | melee | 2.2s | 61.0% | 5.96 | 6.55 | 5.07 | 0.0% |  |
| Mithril Sword | melee | 2.4s | 61.9% | 5.93 | 6.53 | 5.04 | 0.0% |  |
| Mithril Battleaxe | melee | 3.1s | 57.3% | 5.83 | 6.41 | 4.95 | 0.0% |  |
| Stone Hammer | melee | 3.8s | 69.2% | 5.83 | 6.41 | 4.96 | 0.0% | 2H |

**Non-weapon items granting special attacks:**

- **Crystal Throwing Knife** (Quiver) — Crystalline, 30.0% chance
- **Crystal Javelin** (Quiver) — Crystal Cleave, 50.0% chance
- **Crystal Arrows** (Quiver) — Crystal Cleave, 50.0% chance
- **Sapphire Bolts (Enchanted)** (Quiver) — Sapphire Shots, 30.0% chance
- **Sapphire Bolts (Arcane)** (Quiver) — Sapphire Shots, 30.0% chance

## Tier 20-29 — reference level 25

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Maple Longbow | ranged | 3.0s | 67.7% | 8.92 | 10.49 | 11.54 | 0.0% | 2H |
| Adamant 2H Sword | melee | 3.6s | 75.0% | 10.31 | 11.34 | 8.77 | 0.0% | 2H |
| Magical Broomstick | melee | 3.6s | 75.0% | 10.31 | 11.34 | 8.77 | 9.1% | CM 2H |
| Adamant Battleaxe | melee | 3.1s | 60.0% | 9.19 | 10.11 | 7.81 | 0.0% |  |
| Adamant Scimitar | melee | 2.4s | 65.6% | 9.02 | 9.92 | 7.67 | 0.0% |  |
| Adamant Crossbow | ranged | 3.2s | 69.2% | 7.63 | 8.98 | 9.88 | 0.0% |  |
| Adamant Sword | melee | 2.4s | 64.8% | 8.51 | 9.36 | 7.23 | 0.0% |  |
| Maple Shortbow | ranged | 2.6s | 63.2% | 7.23 | 8.51 | 9.36 | 0.0% | 2H |
| Adamant Dagger | melee | 2.2s | 62.8% | 8.13 | 8.95 | 6.91 | 0.0% |  |
| Crystal Battlestaff | magic | 3.0s | 59.5% | 8.84 | 6.83 | 8.03 | 39.4% | 2H |
| Magic Wand (Powerful) | magic | 2.6s | 62.4% | 6.33 | 4.89 | 5.76 | 0.0% |  |
| Air Battlestaff | magic | 3.0s | 59.5% | 5.89 | 4.55 | 5.35 | 0.0% | 2H |
| Water Battlestaff | magic | 3.0s | 59.5% | 5.89 | 4.55 | 5.35 | 0.0% | 2H |
| Earth Battlestaff | magic | 3.0s | 59.5% | 5.89 | 4.55 | 5.35 | 0.0% | 2H |
| Fire Battlestaff | magic | 3.0s | 59.5% | 5.89 | 4.55 | 5.35 | 0.0% | 2H |

## Tier 30-39 — reference level 35

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Granite Mace | melee | 2.8s | 76.8% | 19.61 | 21.57 | 16.67 | 9.1% |  |
| Rune Claw | melee | 2.2s | 71.4% | 19.53 | 21.48 | 16.6 | 26.7% |  |
| Rune Mallet | melee | 3.9s | 80.8% | 18.65 | 20.52 | 15.86 | 0.0% | 2H |
| Ice Shortbow | ranged | 2.6s | 74.2% | 15.04 | 17.69 | 19.46 | 35.5% | 2H |
| Rune 2H Sword | melee | 3.6s | 78.7% | 17.48 | 19.23 | 14.86 | 0.0% | 2H |
| Familiar 2H Sword | melee | 3.6s | 78.7% | 17.48 | 19.23 | 14.86 | 0.0% | 2H |
| Unholy 2H Sword (m) | melee | 3.6s | 78.7% | 17.48 | 19.23 | 14.86 | 0.0% | 2H |
| Elerine Spear | melee | 3.6s | 78.7% | 17.47 | 19.22 | 14.85 | 9.0% | 2H |
| Ice 2H Sword | melee | 3.6s | 75.6% | 16.48 | 18.13 | 14.01 | 9.1% | 2H |
| Mudball Staff | magic | 3.0s | 57.9% | 17.27 | 13.35 | 15.7 | 65.9% | 2H |
| Ice Longbow | ranged | 3.0s | 77.9% | 13.03 | 15.33 | 16.86 | 9.1% | 2H |
| Rune Battleaxe | melee | 3.1s | 63.6% | 15.29 | 16.82 | 13.0 | 0.0% |  |
| Yew Longbow | ranged | 3.0s | 73.3% | 12.78 | 15.03 | 16.54 | 0.0% | 2H |
| Unholy Longbow (m) | ranged | 3.0s | 73.3% | 12.78 | 15.03 | 16.54 | 0.0% | 2H |
| Ice Battleaxe | melee | 3.1s | 63.2% | 14.88 | 16.37 | 12.65 | 9.1% |  |
| Granite Crossbow | ranged | 3.8s | 71.9% | 11.88 | 13.97 | 15.37 | 29.8% |  |

**Non-weapon items granting special attacks:**

- **Ruby Bolts (Enchanted)** (Quiver) — Ruby Shots, 30.0% chance
- **Ruby Bolts (Arcane)** (Quiver) — Ruby Shots, 30.0% chance
- **Earth Wall Shield** (Shield) — Earth Wall, 30.0% chance *(cantMiss)*
- **Poison Bolts** (Quiver) — Poison, 20.0% chance

## Tier 40-49 — reference level 45

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Desert Sabre | melee | 2.4s | 75.0% | 21.69 | 23.86 | 18.44 | 14.2% |  |
| Poison Crossbow | ranged | 3.2s | 74.2% | 18.07 | 21.26 | 23.39 | 29.6% |  |
| Magic Longbow | ranged | 3.0s | 78.2% | 17.18 | 20.21 | 22.23 | 0.0% | 2H |
| Elerine Longbow | ranged | 3.0s | 78.2% | 17.17 | 20.2 | 22.23 | 9.1% | 2H |
| Familiar Longbow | ranged | 3.0s | 78.2% | 17.18 | 20.21 | 22.23 | 0.0% | 2H |
| Pure Crystal Longbow | ranged | 3.0s | 78.2% | 17.18 | 20.21 | 22.23 | 0.0% | 2H |
| Desert Shortbow | ranged | 2.6s | 75.2% | 15.11 | 17.78 | 19.55 | 14.2% | 2H |
| Magic Shortbow | ranged | 2.6s | 74.4% | 13.5 | 15.88 | 17.47 | 0.0% | 2H |
| Pure Crystal Shortbow | ranged | 2.6s | 74.4% | 13.5 | 15.88 | 17.47 | 0.0% | 2H |
| Miolite Sceptre | melee | 2.4s | 69.2% | 15.87 | 17.45 | 13.49 | 9.1% |  |

**Non-weapon items granting special attacks:**

- **Sandstorm Ring** (Ring) — Sandstorm, 15.0% chance *(cantMiss)*

## Tier 50-59 — reference level 55

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Pure Crystal 2H Axe | melee | 3.6s | 83.3% | 89.77 | 98.75 | 76.3 | 67.1% | 2H |
| Pure Crystal 2H Spear | melee | 2.8s | 80.2% | 42.12 | 46.33 | 35.8 | 26.7% | 2H |
| Dragon 2H Sword | melee | 3.6s | 82.1% | 30.23 | 33.25 | 25.69 | 0.0% | 2H |
| Dragon Claw | melee | 2.2s | 73.6% | 27.11 | 29.82 | 23.04 | 21.0% |  |
| Dragon Battleaxe | melee | 3.1s | 67.7% | 26.74 | 29.42 | 22.73 | 0.0% |  |
| Pure Crystal Crossbow | ranged | 3.2s | 75.2% | 22.34 | 26.28 | 28.91 | 22.0% |  |
| Redwood Longbow | ranged | 3.0s | 79.6% | 21.43 | 25.21 | 27.73 | 0.0% | 2H |
| Dragon Scimitar | melee | 2.4s | 75.6% | 23.93 | 26.32 | 20.34 | 0.0% |  |
| Dragon Sword | melee | 2.4s | 75.6% | 23.3 | 25.63 | 19.81 | 0.0% |  |
| Dragon Crossbow | ranged | 3.2s | 75.2% | 19.17 | 22.56 | 24.81 | 0.0% |  |
| Confetti Crossbow | ranged | 3.2s | 75.2% | 19.17 | 22.56 | 24.81 | 0.0% |  |
| Slayer's Crossbow | ranged | 3.2s | 75.2% | 19.17 | 22.56 | 24.81 | 0.0% |  |
| Dragon Dagger | melee | 2.2s | 71.9% | 20.11 | 22.12 | 17.09 | 0.0% |  |
| Redwood Shortbow | ranged | 2.6s | 75.8% | 16.59 | 19.52 | 21.47 | 0.0% | 2H |
| Magic Wand (Elite) | magic | 2.6s | 65.2% | 15.06 | 11.64 | 13.69 | 24.2% |  |
| Poisoned Shortbow | ranged | 2.6s | 75.8% | 0.0 | 0.0 | 0.0 | n/a | ! 2H |

**Non-weapon items granting special attacks:**

- **Pure Crystal Javelin** (Quiver) — Crystal Cleave, 50.0% chance
- **Pure Crystal Throwing Knife** (Quiver) — Crystalline, 30.0% chance
- **Pure Crystal Arrows** (Quiver) — Crystal Cleave, 50.0% chance
- **Emerald Bolts (Enchanted)** (Quiver) — Emerald Shots, 30.0% chance
- **Emerald Bolts (Arcane)** (Quiver) — Emerald Shots, 30.0% chance

## Tier 60-69 — reference level 65

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Impossible Longbow | ranged | 3.0s | 78.5% | 57.06 | 67.13 | 73.85 | 59.6% | 2H |
| Ancient 2H Sword | melee | 3.6s | 82.4% | 51.34 | 56.47 | 43.64 | 30.1% | 2H |
| Warberd | melee | 3.0s | 75.6% | 49.91 | 54.91 | 42.43 | 27.3% | 2H |
| War Axe | melee | 3.3s | 72.6% | 49.72 | 54.7 | 42.27 | 44.1% | 2H |
| Ancient Claw | melee | 2.2s | 76.3% | 41.48 | 45.63 | 35.26 | 30.1% |  |
| Cursed 2H Sword (m) | melee | 3.6s | 83.1% | 37.73 | 41.5 | 32.07 | 0.0% | 2H |
| Ancient Longbow | ranged | 3.0s | 78.5% | 30.53 | 35.91 | 39.51 | 24.5% | CM 2H |
| Twin Exiles | melee | 2.0s | 76.3% | 33.75 | 37.12 | 28.69 | 39.4% | 2H |
| Ancient Crossbow | ranged | 3.2s | 77.1% | 26.33 | 30.98 | 34.07 | 9.1% |  |
| Cursed Longbow (m) | ranged | 3.0s | 80.4% | 25.96 | 30.54 | 33.59 | 0.0% | 2H |
| Ancient Sword | melee | 2.4s | 76.5% | 29.33 | 32.27 | 24.93 | 9.2% |  |
| Pirate Captains Sword | melee | 2.4s | 76.5% | 29.31 | 32.25 | 24.92 | 0.0% |  |
| Sunset Rapier | melee | 2.2s | 76.5% | 29.2 | 32.11 | 24.82 | 9.1% |  |
| Air Imbued Wand | magic | 2.6s | 66.7% | 18.78 | 14.52 | 17.08 | 24.2% |  |
| Water Imbued Wand | magic | 2.6s | 66.7% | 18.78 | 14.52 | 17.08 | 24.2% |  |
| Earth Imbued Wand | magic | 2.6s | 66.7% | 18.78 | 14.52 | 17.08 | 24.2% |  |

**Non-weapon items granting special attacks:**

- **Ultimate Slapping Gloves** (Gloves) — Unlimited Slapping Power, 100.0% chance
- **Enchanted Diamond Bolts** (Quiver) — Diamond Shots, 30.0% chance
- **Burning Ring** (Ring) — Burn, 20.0% chance
- **Fire Arrows** (Quiver) — Burn, 20.0% chance

## Tier 70-79 — reference level 75

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Big ol Ron | melee | 3.6s | 84.2% | 57.63 | 63.39 | 48.98 | 0.0% | 2H |
| Infernal Claw | melee | 2.2s | 77.3% | 54.52 | 59.97 | 46.34 | 37.3% |  |
| Sanguine Blade | melee | 3.6s | 83.0% | 46.22 | 50.84 | 39.28 | 9.1% | 2H |
| Ghost Blunderbow | ranged | 3.0s | 77.8% | 37.94 | 44.63 | 49.1 | 28.7% |  |
| Ghost Scimitar | melee | 2.4s | 76.3% | 41.02 | 45.12 | 34.86 | 30.2% |  |
| Soul Taker Wand | magic | 2.6s | 67.7% | 44.38 | 34.29 | 40.35 | 63.0% |  |
| Ancient Hunting Bow | ranged | 3.0s | 79.1% | 32.63 | 38.39 | 42.23 | 17.9% | CM 2H |
| Water Sceptre | melee | 2.4s | 77.8% | 36.78 | 40.46 | 31.27 | 0.0% |  |
| Darksteel Dagger | melee | 2.2s | 74.2% | 28.5 | 31.35 | 24.22 | 9.1% |  |
| Rotten Staff | magic | 3.0s | 63.2% | 29.21 | 22.57 | 26.55 | 54.6% | 2H |
| Lich Staff | magic | 3.0s | 63.6% | 26.34 | 20.35 | 23.95 | 56.1% | CM 2H |
| Foresight Wand | magic | 3.0s | 64.8% | 14.97 | 11.57 | 13.61 | 9.0% |  |
| Stormsnap | ranged | 3.0s | 50.0% | 5.55 | 6.53 | 7.19 | 0.0% | CM ! 2H |

**Non-weapon items granting special attacks:**

- **Diamond Bolts (Enchanted)** (Quiver) — Diamond Shots, 30.0% chance
- **Diamond Bolts (Arcane)** (Quiver) — Diamond Shots, 30.0% chance
- **Darksteel Arrows** (Quiver) — Deadly Cut, 100.0% chance

## Tier 80-89 — reference level 85

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Engulfing Vortex Longbow | ranged | 3.0s | 79.2% | 211.28 | 248.57 | 273.42 | 87.9% | 2H |
| Ocean Song | magic | 2.6s | 68.6% | 219.06 | 169.27 | 199.14 | 87.8% | CM |
| Ultima Godsword | melee | 3.8s | 86.6% | 152.69 | 167.96 | 129.79 | 53.3% | CM ! 2H |
| Ragnar Godsword | melee | 3.8s | 84.7% | 121.9 | 134.09 | 103.62 | 46.1% | CM 2H |
| Aeris Godsword | melee | 3.2s | 84.7% | 90.61 | 99.67 | 77.02 | 33.9% | 2H |
| Water Pulse Staff | magic | 3.0s | 71.7% | 88.0 | 68.0 | 80.0 | 78.3% | CM 2H |
| Hasty Trident | melee | 3.2s | 84.3% | 77.72 | 85.49 | 66.06 | 9.1% | 2H |
| Shockwave | ranged | 3.2s | 77.9% | 62.55 | 73.59 | 80.95 | 49.8% | CM |
| Glacia Godsword | melee | 3.4s | 84.7% | 65.95 | 72.54 | 56.05 | 14.5% | CM 2H |
| Cloudburst Staff | magic | 3.0s | 70.6% | 70.25 | 54.29 | 63.87 | 74.0% | 2H |
| Dark Steel 2H Sword | melee | 3.2s | 83.9% | 61.1 | 67.21 | 51.94 | 9.1% | 2H |
| Terran Godsword | melee | 3.6s | 84.7% | 56.99 | 62.69 | 48.44 | 0.0% | CM ! 2H |
| Tidal Edge | melee | 2.4s | 82.6% | 34.46 | 37.91 | 29.29 | 0.0% | CM ! |
| Mystery Wand | magic | 2.6s | 66.7% | 23.02 | 17.79 | 20.93 | 24.3% |  |

**Non-weapon items granting special attacks:**

- **Dragon Head Helmet** (Helmet) — Firebreathing, 20.0% chance *(cantMiss)*
- **Enchanted Jadestone Bolts** (Quiver) — Jadestone Shots, 30.0% chance
- **Jadestone Bolts (Enchanted)** (Quiver) — Jadestone Shots, 30.0% chance
- **Jadestone Bolts (Arcane)** (Quiver) — Jadestone Shots, 30.0% chance

## Tier 90-99 — reference level 95

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Heated_Fury 2H Hammer | melee | 3.6s | 87.9% | 284.43 | 312.87 | 241.77 | 64.7% | 2H |
| Corundum 2H Sword | melee | 3.6s | 84.4% | 75.81 | 83.39 | 64.44 | 24.2% | 2H |
| Corundum Crossbow | ranged | 3.2s | 79.9% | 49.27 | 57.96 | 63.75 | 24.2% |  |
| Corundum Battleaxe | melee | 3.1s | 69.5% | 57.73 | 63.5 | 49.07 | 24.2% |  |
| Corundum Sword | melee | 2.4s | 78.7% | 54.08 | 59.49 | 45.97 | 24.2% |  |
| Corundum Scimitar | melee | 2.4s | 77.6% | 49.29 | 54.22 | 41.9 | 24.2% |  |
| Corundum Dagger | melee | 2.2s | 76.5% | 46.51 | 51.16 | 39.53 | 24.2% |  |
| Elderwood Longbow | ranged | 3.0s | 79.6% | 34.7 | 40.82 | 44.91 | 13.4% | ! 2H |
| Elderwood Shortbow | ranged | 2.6s | 75.8% | 26.66 | 31.36 | 34.5 | 13.4% | ! 2H |
| Poison Staff | magic | 3.0s | 68.9% | 28.31 | 21.87 | 25.73 | 0.0% | 2H |

**Non-weapon items granting special attacks:**

- **Corundum Javelin** (Quiver) — CorundumWounds, 5.0% chance
- **Corundum Throwing Knife** (Quiver) — CorundumWounds, 5.0% chance
- **Dark Blade Defender** (Shield) — Dark Blade, 20.0% chance
- **Hood of Shade Summon** (Helmet) — Shade Summon, 40.0% chance

## Tier 100-109 — reference level 105

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| FrostSpark 1H Sword | melee | 2.4s | 85.7% | 457.73 | 503.5 | 389.07 | 84.6% |  |
| Royal Toxins Spear | melee | 3.2s | 91.1% | 410.84 | 451.93 | 349.22 | 69.7% | 2H |
| Lightning Coil 2H Staff | magic | 3.0s | 71.4% | 372.66 | 287.97 | 338.79 | 91.6% | CM 2H |
| Lightning Strike 1H Sword | melee | 2.4s | 84.3% | 298.61 | 328.47 | 253.82 | 78.6% |  |
| Thorned Power Bow | ranged | 3.0s | 85.4% | 251.65 | 296.05 | 325.66 | 76.5% | CM 2H |
| Meteorite 2H Sword | melee | 3.6s | 87.6% | 231.16 | 254.27 | 196.48 | 63.6% | 2H |
| Spectral Ice Sword | melee | 2.4s | 84.3% | 207.27 | 228.0 | 176.18 | 69.2% |  |
| Torrential Blast Crossbow | ranged | 3.2s | 86.9% | 122.28 | 143.85 | 158.24 | 53.4% | CM |
| Divine 2H Sword | melee | 3.6s | 88.9% | 110.66 | 121.72 | 94.06 | 13.4% | 2H |
| Augite 2H Sword | melee | 3.6s | 86.3% | 91.3 | 100.43 | 77.6 | 19.1% | CM 2H |
| Divine Battleaxe | melee | 3.1s | 73.3% | 73.89 | 81.28 | 62.81 | 13.4% |  |
| Augite Battleaxe | melee | 3.1s | 71.7% | 71.57 | 78.73 | 60.84 | 21.6% | CM |
| Divine Crossbow | ranged | 3.2s | 85.4% | 60.37 | 71.03 | 78.13 | 13.4% |  |
| Divine Sword | melee | 2.4s | 82.4% | 65.62 | 72.19 | 55.78 | 13.4% |  |
| Augite Crossbow | ranged | 3.2s | 81.8% | 54.93 | 64.62 | 71.08 | 19.8% | CM |
| Augite Sword | melee | 2.4s | 80.8% | 63.68 | 70.05 | 54.13 | 19.9% | CM |

**Non-weapon items granting special attacks:**

- **Divine Javelin** (Quiver) — Divine Breaker, 5.0% chance
- **Augite Javelin** (Quiver) — Augite Crystallization, 5.0% chance *(cantMiss)*
- **Augite Throwing Knife** (Quiver) — Augite Crystallization, 5.0% chance *(cantMiss)*
- **Divine Throwing Knife** (Quiver) — Divine Breaker, 5.0% chance
- **Gloves of Greater Shade Summon** (Gloves) — Greater Shade Summon, 20.0% chance
- **Ring of Phantom Summon** (Ring) — Phantom Summon, 20.0% chance
- **Burning Embers Book** (Shield) — Burning Embers, 5.0% chance *(cantMiss)*

## Tier 110-120 — reference level 115

| Weapon | Style | Spd | Hit% | vs Melee | vs Ranged | vs Magic | spec% | flags |
|---|---|---|---|---|---|---|---|---|
| Feather Storm Crossbow | ranged | 3.2s | 88.5% | 413.05 | 485.94 | 534.53 | 83.5% |  |
| Ethereal Greataxe | melee | 3.6s | 91.4% | 391.34 | 430.48 | 332.64 | 69.3% | CM 2H |
| Agile Wings Rapier | melee | 2.2s | 88.2% | 259.59 | 285.55 | 220.65 | 60.0% |  |
| Ethereal Longbow | ranged | 3.2s | 83.3% | 120.36 | 141.6 | 155.76 | 68.7% | CM 2H |
| Meteorite Crossbow | ranged | 3.2s | 83.7% | 113.85 | 133.94 | 147.34 | 54.5% |  |
| Slicing Maelstrom Wand | magic | 2.6s | 75.2% | 48.2 | 37.24 | 43.81 | 0.0% |  |
| Calamity Wand | magic | 2.6s | 69.8% | 47.85 | 36.97 | 43.5 | 24.2% |  |
| Ethereal Staff | magic | 3.0s | 73.3% | 38.18 | 29.5 | 34.71 | 0.0% | 2H |

**Non-weapon items granting special attacks:**

- **Meteorite Javelin** (Quiver) — Meteor Shot, 50.0% chance
- **Meteorite Bolts** (Quiver) — Meteor Shot, 50.0% chance
- **Amulet of Curse Totem Summon** (Amulet) — Curse Totem Summon, 20.0% chance

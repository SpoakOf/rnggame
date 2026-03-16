# Loot Rush RNG (Tkinter)

A GUI-based RNG game where players open **Card Packs**, **Treasure Chests**, and **Gun Cases** to collect items with rarities:

- Common
- Rare
- Epic
- Legendary
- Mythic

Each item has a sell value. Sell items to earn currency, then upgrade sources and luck to improve rare drop chances.

## Features

- Fully GUI-driven loop with animated reveal phases.
- Three loot source types with independent tier progression.
- Inventory management with sell selected / auto-sell low-tier items.
- Luck upgrades that shift weighted rarity outcomes over time.
- Dynamic rarity highlights and drop chance readouts.

## Run

```bash
python3 game.py
```

No third-party dependencies are required (uses Python standard library `tkinter`).

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk


RARITY_COLORS = {
    "Common": "#cfd8dc",
    "Rare": "#64b5f6",
    "Epic": "#ba68c8",
    "Legendary": "#ffb74d",
    "Mythic": "#ef5350",
}

RARITY_BASE_VALUES = {
    "Common": 10,
    "Rare": 35,
    "Epic": 120,
    "Legendary": 420,
    "Mythic": 1200,
}


@dataclass
class Item:
    name: str
    rarity: str
    value: int

    def display(self) -> str:
        return f"{self.name} ({self.rarity}) - ${self.value}"


@dataclass
class Source:
    name: str
    base_cost: int
    tier: int = 1

    def open_cost(self) -> int:
        return int(self.base_cost * (1 + (self.tier - 1) * 0.9))

    def upgrade_cost(self) -> int:
        return int(self.base_cost * (self.tier + 1) * 5)


class RNGGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Loot Rush RNG")
        self.root.geometry("1120x700")
        self.root.configure(bg="#10131a")

        self.currency = 250
        self.luck_level = 1
        self.luck_bonus = 0.0
        self.inventory: list[Item] = []

        self.sources = {
            "Card Pack": Source("Card Pack", base_cost=45),
            "Treasure Chest": Source("Treasure Chest", base_cost=95),
            "Gun Case": Source("Gun Case", base_cost=170),
        }

        self.item_pools = {
            "Card Pack": {
                "Common": ["Rookie Forward", "City Guard", "Arcane Scout", "Speedster", "Copper Mage"],
                "Rare": ["All-Star Playmaker", "Neon Defender", "Galactic Dribbler", "Skyline Sniper"],
                "Epic": ["MVP Tactician", "Shadow Captain", "Solar Striker"],
                "Legendary": ["Hall-of-Fame Icon", "Infinite Ace"],
                "Mythic": ["Celestial Legend"],
            },
            "Treasure Chest": {
                "Common": ["Rusty Compass", "Old Coin Stack", "Traveler's Band"],
                "Rare": ["Jeweled Goblet", "Emerald Relic", "Pirate Medallion"],
                "Epic": ["Cursed Crown", "Ancient Ruby Idol"],
                "Legendary": ["Dragon Hoard Sigil", "Sunken Emperor Crown"],
                "Mythic": ["Heart of Atlantis"],
            },
            "Gun Case": {
                "Common": ["Urban Pistol Skin", "Steel Trigger", "Dust Camo"],
                "Rare": ["Neon Burst SMG", "Crimson Barrel", "Glacier Scope"],
                "Epic": ["Vortex Rifle", "Phoenix Shotgun"],
                "Legendary": ["Obsidian Reaper", "Aurora Sniper"],
                "Mythic": ["Abyssal Dragonblade"],
            },
        }

        self.styles()
        self.build_layout()
        self.refresh_ui()

    def styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TLabel", background="#10131a", foreground="#f4f7ff", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", background="#10131a", foreground="#b8c0d4", font=("Segoe UI", 10))
        style.configure("Card.TFrame", background="#1a1f2b", relief="flat")
        style.configure("Game.TButton", font=("Segoe UI", 10, "bold"), padding=8)

    def build_layout(self) -> None:
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left: opening and progression
        self.left_panel = ttk.Frame(self.root, style="Card.TFrame", padding=16)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=14)
        self.left_panel.columnconfigure(0, weight=1)

        ttk.Label(self.left_panel, text="Loot Rush RNG", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        self.stat_label = ttk.Label(self.left_panel, text="", style="Sub.TLabel")
        self.stat_label.grid(row=1, column=0, sticky="w", pady=(0, 14))

        self.source_frame = ttk.Frame(self.left_panel, style="Card.TFrame")
        self.source_frame.grid(row=2, column=0, sticky="ew")
        self.source_frame.columnconfigure(0, weight=1)

        self.reveal_panel = tk.Frame(self.left_panel, bg="#121725", highlightthickness=2, highlightbackground="#2a3144")
        self.reveal_panel.grid(row=3, column=0, sticky="nsew", pady=18)
        self.left_panel.rowconfigure(3, weight=1)

        self.reveal_status = tk.Label(
            self.reveal_panel,
            text="Pick a source and open for loot!",
            bg="#121725",
            fg="#f4f7ff",
            font=("Segoe UI", 18, "bold"),
        )
        self.reveal_status.pack(expand=True)

        self.reveal_hint = tk.Label(
            self.reveal_panel,
            text="Sell drops for cash, upgrade tiers, and increase luck to chase Mythics.",
            bg="#121725",
            fg="#9da8c3",
            font=("Segoe UI", 10),
        )
        self.reveal_hint.pack(pady=(0, 18))

        # Right: inventory and controls
        self.right_panel = ttk.Frame(self.root, style="Card.TFrame", padding=16)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=14)
        self.right_panel.rowconfigure(2, weight=1)
        self.right_panel.columnconfigure(0, weight=1)

        ttk.Label(self.right_panel, text="Inventory", style="Header.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.right_panel, text="Manage drops, sell items, and optimize progression.", style="Sub.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 8)
        )

        self.inventory_list = tk.Listbox(
            self.right_panel,
            bg="#0f1320",
            fg="#f4f7ff",
            selectbackground="#2f6feb",
            font=("Consolas", 10),
            height=22,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#2a3144",
        )
        self.inventory_list.grid(row=2, column=0, sticky="nsew")

        control = ttk.Frame(self.right_panel, style="Card.TFrame")
        control.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        control.columnconfigure((0, 1), weight=1)

        self.sell_selected_btn = ttk.Button(control, text="Sell Selected", style="Game.TButton", command=self.sell_selected)
        self.sell_selected_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.sell_all_btn = ttk.Button(control, text="Sell All Commons/Rares", style="Game.TButton", command=self.sell_low_tier)
        self.sell_all_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.luck_btn = ttk.Button(self.right_panel, text="Upgrade Luck", style="Game.TButton", command=self.upgrade_luck)
        self.luck_btn.grid(row=4, column=0, sticky="ew", pady=(10, 0))

        self.inventory_value_label = ttk.Label(self.right_panel, text="", style="Sub.TLabel")
        self.inventory_value_label.grid(row=5, column=0, sticky="w", pady=(8, 0))

        self.source_widgets: dict[str, dict[str, ttk.Widget]] = {}
        for i, source_name in enumerate(self.sources.keys()):
            box = ttk.Frame(self.source_frame, style="Card.TFrame", padding=8)
            box.grid(row=i, column=0, sticky="ew", pady=4)
            box.columnconfigure(0, weight=1)

            title = ttk.Label(box, text=source_name, style="Header.TLabel")
            title.grid(row=0, column=0, sticky="w")

            details = ttk.Label(box, text="", style="Sub.TLabel")
            details.grid(row=1, column=0, sticky="w", pady=(0, 6))

            actions = ttk.Frame(box, style="Card.TFrame")
            actions.grid(row=2, column=0, sticky="ew")
            actions.columnconfigure((0, 1), weight=1)

            open_btn = ttk.Button(actions, text="Open", style="Game.TButton", command=lambda n=source_name: self.open_source(n))
            open_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

            upgrade_btn = ttk.Button(actions, text="Upgrade Tier", style="Game.TButton", command=lambda n=source_name: self.upgrade_source(n))
            upgrade_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

            self.source_widgets[source_name] = {"details": details, "open": open_btn, "upgrade": upgrade_btn}

    def current_drop_weights(self, source: Source) -> dict[str, float]:
        tier_bonus = (source.tier - 1) * 0.03
        luck_bonus = self.luck_bonus

        common = max(0.3, 64 - source.tier * 4 - luck_bonus * 120)
        rare = 24 + source.tier * 2 + luck_bonus * 45
        epic = 9 + tier_bonus * 100 + luck_bonus * 50
        legendary = 2.6 + tier_bonus * 60 + luck_bonus * 25
        mythic = 0.4 + tier_bonus * 28 + luck_bonus * 16

        weights = {
            "Common": common,
            "Rare": rare,
            "Epic": epic,
            "Legendary": legendary,
            "Mythic": mythic,
        }
        return weights

    def weighted_roll(self, weights: dict[str, float]) -> str:
        rarities = list(weights.keys())
        values = [max(0.01, w) for w in weights.values()]
        return random.choices(rarities, weights=values, k=1)[0]

    def open_source(self, source_name: str) -> None:
        source = self.sources[source_name]
        cost = source.open_cost()
        if self.currency < cost:
            self.flash_message("Not enough currency! Sell loot or open cheaper sources.", "#f44336")
            return

        self.currency -= cost
        weights = self.current_drop_weights(source)
        rarity = self.weighted_roll(weights)

        item_name = random.choice(self.item_pools[source_name][rarity])
        base = RARITY_BASE_VALUES[rarity]
        tier_multiplier = 1 + (source.tier - 1) * 0.28
        variance = random.uniform(0.9, 1.3)
        value = int(base * tier_multiplier * variance)
        new_item = Item(item_name, rarity, value)
        self.inventory.append(new_item)

        self.play_open_animation(source_name, new_item)
        self.refresh_ui()

    def play_open_animation(self, source_name: str, item: Item) -> None:
        phases = [
            f"Cracking open {source_name}.",
            f"Cracking open {source_name}..",
            f"Cracking open {source_name}...",
            "Scanning loot matrix...",
            "Revealing item!",
        ]

        def step(i: int) -> None:
            if i < len(phases):
                self.reveal_status.config(text=phases[i], fg="#f4f7ff", bg="#121725")
                self.reveal_panel.config(bg="#121725", highlightbackground="#2a3144")
                self.reveal_hint.config(text="")
                self.root.after(120, lambda: step(i + 1))
            else:
                color = RARITY_COLORS[item.rarity]
                self.reveal_panel.config(bg="#0d1019", highlightbackground=color)
                self.reveal_status.config(text=item.display(), fg=color, bg="#0d1019")
                self.reveal_hint.config(
                    text=f"{item.rarity} drop! This item sells for ${item.value}.", fg="#d7def2", bg="#0d1019"
                )

        step(0)

    def upgrade_source(self, source_name: str) -> None:
        source = self.sources[source_name]
        cost = source.upgrade_cost()
        if self.currency < cost:
            self.flash_message(f"Need ${cost} to upgrade {source_name}.", "#ff7043")
            return
        self.currency -= cost
        source.tier += 1
        self.flash_message(f"{source_name} upgraded to Tier {source.tier}!", "#66bb6a")
        self.refresh_ui()

    def upgrade_luck(self) -> None:
        cost = int(220 * (1.65 ** (self.luck_level - 1)))
        if self.currency < cost:
            self.flash_message(f"Need ${cost} for luck upgrade.", "#ff7043")
            return

        self.currency -= cost
        self.luck_level += 1
        self.luck_bonus += 0.012
        self.flash_message(f"Luck increased to Lv {self.luck_level}! Better odds unlocked.", "#81c784")
        self.refresh_ui()

    def sell_selected(self) -> None:
        selection = self.inventory_list.curselection()
        if not selection:
            self.flash_message("Select an item in inventory to sell.", "#fdd835")
            return

        idx = selection[0]
        item = self.inventory.pop(idx)
        self.currency += item.value
        self.flash_message(f"Sold {item.name} for ${item.value}.", "#4dd0e1")
        self.refresh_ui()

    def sell_low_tier(self) -> None:
        remaining: list[Item] = []
        sold_total = 0
        sold_count = 0
        for item in self.inventory:
            if item.rarity in {"Common", "Rare"}:
                sold_total += item.value
                sold_count += 1
            else:
                remaining.append(item)

        if sold_count == 0:
            self.flash_message("No Common/Rare items to sell.", "#fdd835")
            return

        self.inventory = remaining
        self.currency += sold_total
        self.flash_message(f"Auto-sold {sold_count} items for ${sold_total}.", "#4dd0e1")
        self.refresh_ui()

    def flash_message(self, text: str, color: str) -> None:
        self.reveal_panel.config(bg="#121725", highlightbackground=color)
        self.reveal_status.config(text=text, fg=color, bg="#121725")
        self.reveal_hint.config(text="Keep opening and upgrading for bigger drops!", fg="#9da8c3", bg="#121725")

    def refresh_ui(self) -> None:
        inv_value = sum(item.value for item in self.inventory)
        self.stat_label.config(
            text=(
                f"Currency: ${self.currency}   |   Luck Lv {self.luck_level} (+{self.luck_bonus * 100:.1f}% hidden rarity boost)"
            )
        )
        self.inventory_value_label.config(text=f"Items: {len(self.inventory)}   |   Total Inventory Value: ${inv_value}")

        self.inventory_list.delete(0, tk.END)
        for item in self.inventory:
            self.inventory_list.insert(tk.END, item.display())

        for source_name, source in self.sources.items():
            weights = self.current_drop_weights(source)
            total = sum(weights.values())
            mythic_chance = weights["Mythic"] / total * 100
            legendary_chance = weights["Legendary"] / total * 100
            details = (
                f"Tier {source.tier} | Open: ${source.open_cost()} | Upgrade: ${source.upgrade_cost()} | "
                f"Legendary: {legendary_chance:.2f}% | Mythic: {mythic_chance:.2f}%"
            )
            self.source_widgets[source_name]["details"].config(text=details)


if __name__ == "__main__":
    root = tk.Tk()
    game = RNGGame(root)
    root.mainloop()

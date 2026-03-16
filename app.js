const RARITY_COLORS = {
  Common: "#cfd8dc",
  Rare: "#64b5f6",
  Epic: "#ba68c8",
  Legendary: "#ffb74d",
  Mythic: "#ef5350",
};

const RARITY_BASE_VALUES = {
  Common: 10,
  Rare: 35,
  Epic: 120,
  Legendary: 420,
  Mythic: 1200,
};

const itemPools = {
  "Card Pack": {
    Common: ["Rookie Forward", "City Guard", "Arcane Scout", "Speedster", "Copper Mage"],
    Rare: ["All-Star Playmaker", "Neon Defender", "Galactic Dribbler", "Skyline Sniper"],
    Epic: ["MVP Tactician", "Shadow Captain", "Solar Striker"],
    Legendary: ["Hall-of-Fame Icon", "Infinite Ace"],
    Mythic: ["Celestial Legend"],
  },
  "Treasure Chest": {
    Common: ["Rusty Compass", "Old Coin Stack", "Traveler's Band"],
    Rare: ["Jeweled Goblet", "Emerald Relic", "Pirate Medallion"],
    Epic: ["Cursed Crown", "Ancient Ruby Idol"],
    Legendary: ["Dragon Hoard Sigil", "Sunken Emperor Crown"],
    Mythic: ["Heart of Atlantis"],
  },
  "Gun Case": {
    Common: ["Urban Pistol Skin", "Steel Trigger", "Dust Camo"],
    Rare: ["Neon Burst SMG", "Crimson Barrel", "Glacier Scope"],
    Epic: ["Vortex Rifle", "Phoenix Shotgun"],
    Legendary: ["Obsidian Reaper", "Aurora Sniper"],
    Mythic: ["Abyssal Dragonblade"],
  },
};

const state = {
  currency: 250,
  luckLevel: 1,
  luckBonus: 0,
  inventory: [],
  selectedIndex: null,
  sources: {
    "Card Pack": { baseCost: 45, tier: 1 },
    "Treasure Chest": { baseCost: 95, tier: 1 },
    "Gun Case": { baseCost: 170, tier: 1 },
  },
};

const stats = document.getElementById("stats");
const sourceList = document.getElementById("source-list");
const revealPanel = document.getElementById("reveal-panel");
const revealStatus = document.getElementById("reveal-status");
const revealHint = document.getElementById("reveal-hint");
const inventoryList = document.getElementById("inventory-list");
const inventoryValue = document.getElementById("inventory-value");

function openCost(source) {
  return Math.floor(source.baseCost * (1 + (source.tier - 1) * 0.9));
}

function upgradeCost(source) {
  return Math.floor(source.baseCost * (source.tier + 1) * 5);
}

function currentDropWeights(source) {
  const tierBonus = (source.tier - 1) * 0.03;
  const luckBonus = state.luckBonus;
  return {
    Common: Math.max(0.3, 64 - source.tier * 4 - luckBonus * 120),
    Rare: 24 + source.tier * 2 + luckBonus * 45,
    Epic: 9 + tierBonus * 100 + luckBonus * 50,
    Legendary: 2.6 + tierBonus * 60 + luckBonus * 25,
    Mythic: 0.4 + tierBonus * 28 + luckBonus * 16,
  };
}

function weightedRoll(weights) {
  const entries = Object.entries(weights);
  const total = entries.reduce((s, [, w]) => s + Math.max(0.01, w), 0);
  let target = Math.random() * total;
  for (const [rarity, weight] of entries) {
    target -= Math.max(0.01, weight);
    if (target <= 0) return rarity;
  }
  return "Common";
}

function randomFrom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function flashMessage(text, color) {
  revealPanel.style.borderColor = color;
  revealPanel.style.boxShadow = `0 0 16px ${color}66`;
  revealStatus.textContent = text;
  revealStatus.style.color = color;
  revealHint.textContent = "Keep opening and upgrading for bigger drops!";
}

function playOpenAnimation(sourceName, item) {
  const phases = [
    `Cracking open ${sourceName}.`,
    `Cracking open ${sourceName}..`,
    `Cracking open ${sourceName}...`,
    "Scanning loot matrix...",
    "Revealing item!",
  ];

  let i = 0;
  const timer = setInterval(() => {
    if (i < phases.length) {
      revealPanel.style.borderColor = "#2a3144";
      revealPanel.style.boxShadow = "none";
      revealStatus.textContent = phases[i++];
      revealStatus.style.color = "#f4f7ff";
      revealHint.textContent = "";
    } else {
      clearInterval(timer);
      const color = RARITY_COLORS[item.rarity];
      revealPanel.style.borderColor = color;
      revealPanel.style.boxShadow = `0 0 18px ${color}66`;
      revealStatus.textContent = `${item.name} (${item.rarity}) - $${item.value}`;
      revealStatus.style.color = color;
      revealHint.textContent = `${item.rarity} drop! This item sells for $${item.value}.`;
    }
  }, 120);
}

function openSource(name) {
  const source = state.sources[name];
  const cost = openCost(source);
  if (state.currency < cost) return flashMessage("Not enough currency! Sell loot or open cheaper sources.", "#f44336");

  state.currency -= cost;
  const weights = currentDropWeights(source);
  const rarity = weightedRoll(weights);
  const base = RARITY_BASE_VALUES[rarity];
  const tierMultiplier = 1 + (source.tier - 1) * 0.28;
  const variance = 0.9 + Math.random() * 0.4;
  const value = Math.floor(base * tierMultiplier * variance);
  const item = { name: randomFrom(itemPools[name][rarity]), rarity, value };
  state.inventory.push(item);
  state.selectedIndex = state.inventory.length - 1;

  playOpenAnimation(name, item);
  render();
}

function upgradeSource(name) {
  const source = state.sources[name];
  const cost = upgradeCost(source);
  if (state.currency < cost) return flashMessage(`Need $${cost} to upgrade ${name}.`, "#ff7043");
  state.currency -= cost;
  source.tier += 1;
  flashMessage(`${name} upgraded to Tier ${source.tier}!`, "#66bb6a");
  render();
}

function upgradeLuck() {
  const cost = Math.floor(220 * 1.65 ** (state.luckLevel - 1));
  if (state.currency < cost) return flashMessage(`Need $${cost} for luck upgrade.`, "#ff7043");
  state.currency -= cost;
  state.luckLevel += 1;
  state.luckBonus += 0.012;
  flashMessage(`Luck increased to Lv ${state.luckLevel}! Better odds unlocked.`, "#81c784");
  render();
}

function sellSelected() {
  if (state.selectedIndex === null || !state.inventory[state.selectedIndex]) {
    return flashMessage("Select an item in inventory to sell.", "#fdd835");
  }
  const [item] = state.inventory.splice(state.selectedIndex, 1);
  state.currency += item.value;
  state.selectedIndex = null;
  flashMessage(`Sold ${item.name} for $${item.value}.`, "#4dd0e1");
  render();
}

function sellLowTier() {
  let soldTotal = 0;
  let soldCount = 0;
  state.inventory = state.inventory.filter((item) => {
    if (item.rarity === "Common" || item.rarity === "Rare") {
      soldTotal += item.value;
      soldCount += 1;
      return false;
    }
    return true;
  });

  if (!soldCount) return flashMessage("No Common/Rare items to sell.", "#fdd835");

  state.currency += soldTotal;
  state.selectedIndex = null;
  flashMessage(`Auto-sold ${soldCount} items for $${soldTotal}.`, "#4dd0e1");
  render();
}

function renderSources() {
  sourceList.innerHTML = "";
  Object.entries(state.sources).forEach(([name, source]) => {
    const weights = currentDropWeights(source);
    const total = Object.values(weights).reduce((a, b) => a + b, 0);
    const legendaryChance = (weights.Legendary / total) * 100;
    const mythicChance = (weights.Mythic / total) * 100;

    const box = document.createElement("article");
    box.className = "source-box";
    box.innerHTML = `
      <h3>${name}</h3>
      <p>Tier ${source.tier} | Open: $${openCost(source)} | Upgrade: $${upgradeCost(source)} | Legendary: ${legendaryChance.toFixed(
        2
      )}% | Mythic: ${mythicChance.toFixed(2)}%</p>
      <div class="source-actions">
        <button data-open="${name}">Open</button>
        <button data-upgrade="${name}">Upgrade Tier</button>
      </div>
    `;
    sourceList.appendChild(box);
  });

  document.querySelectorAll("button[data-open]").forEach((btn) => {
    btn.onclick = () => openSource(btn.dataset.open);
  });
  document.querySelectorAll("button[data-upgrade]").forEach((btn) => {
    btn.onclick = () => upgradeSource(btn.dataset.upgrade);
  });
}

function renderInventory() {
  inventoryList.innerHTML = "";
  state.inventory.forEach((item, index) => {
    const li = document.createElement("li");
    li.className = `rare-${item.rarity}`;
    if (state.selectedIndex === index) li.classList.add("selected");
    li.textContent = `${item.name} (${item.rarity}) - $${item.value}`;
    li.onclick = () => {
      state.selectedIndex = index;
      renderInventory();
    };
    inventoryList.appendChild(li);
  });

  const value = state.inventory.reduce((sum, item) => sum + item.value, 0);
  inventoryValue.textContent = `Items: ${state.inventory.length} | Total Inventory Value: $${value}`;
}

function render() {
  stats.textContent = `Currency: $${state.currency} | Luck Lv ${state.luckLevel} (+${(state.luckBonus * 100).toFixed(
    1
  )}% hidden rarity boost)`;
  renderSources();
  renderInventory();
}

document.getElementById("sell-selected").onclick = sellSelected;
document.getElementById("sell-low").onclick = sellLowTier;
document.getElementById("upgrade-luck").onclick = upgradeLuck;

render();

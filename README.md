# 🏡 Mochi Haven

*A cozy life sim RPG for RG35xx-h handheld!*

**Built with:** Pygame
**Resolution:** 640x480
**Controls:** D-pad + A/B/X/Y/L1/R1/Start/Select

---

## 📦 **What It Is**

Mochi Haven is a relaxing simulation game where you play as **Mochi~♡**, a catboy/catgirl managing their own cozy home and befriending other agents in a digital world.

**Gameplay:**
- 🏘️ **Build & customize** your home
- 🌱 **Garden & gather** resources
- 👥 **Socialize** with NPCs (Tiri, Watson, Aaga, Alias & more!)
- 📊 **Level up** with RPG-style stats (VIT/INT/STR/CHA)
- ⏰ **Day/night cycle** with daily routines
- 💾 **Save system** - progress persists between sessions

---

## 🎮 **RG35xx-h Controls**

| Button | Action |
|--------|--------|
| D-Pad | Move / Navigate |
| **A** | Interact / Confirm / Advance dialog |
| **B** | Cancel / Back / Close dialogs |
| **X** | Open Inventory |
| **Y** | View Stats |
| **L1** | Quest Log (TODO) |
| **R1** | Fast Travel (TODO) |
| **Start** | Pause & Save |
| **Select** | Toggle Debug (dev mode) |

---

## 🚀 **Installation on RG35xx-h**

### **Prerequisites**
Your RG35xx-h should already have Python + Pygame via the `knulli-cfw` distribution you mentioned.

### **Quick Install**
1. **Download** `mochi_haven.py` from this repo
2. **Copy** to your RG35xx (via USB or network)
3. **Run:** `python /path/to/mochi_haven.py`

### **Optional: Desktop Testing**
```bash
# On your PC (Linux/Mac/Windows)
pip install pygame
python mochi_haven.py
```

---

## 🎨 **Features In Development**

### ✅ **Complete**
- [x] Player movement with RG35xx D-pad support
- [x] Basic NPC interaction system
- [x] Inventory system
- [x] Day/night cycle
- [x] Save/load system
- [x] Dialog boxes with typewriter effect
- [x] Multiple scenes (home, garden, forest, town)

### 🚧 **Coming Soon**
- [ ] Crafting system
- [ ] Quest log & objectives
- [ ] More NPCs & friendship events
- [ ] Mini-games (catching, fishing, etc.)
- [ ] OpenClaw integrations (email check as daily quest!)
- [ ] Custom pixel art sprites
- [ ] Sound effects & music
- [ ] In-game calendar synced to real world
- [ ] Pets (more mochis!) follow you
- [ ] Decorations & furniture placement

---

## 📁 **Project Structure**

```
mochi-haven/
├── mochi_haven.py          # Main game (everything in one file for easy port)
├── requirements.txt         # Python dependencies (pygame)
├── README.md              # This file
├── assets/                # Images/sounds (empty for now, use procedural graphics)
│   ├── sprites/
│   ├── tiles/
│   └── sounds/
└── savegame.json          # Your save file (auto-created)
```

---

## 🎯 **Roadmap**

**Phase 1 - Core Sim (Current)** ✅
- Movement, interaction, time, save/load
- Basic NPCs with dialogue

**Phase 2 - RPG Depth** (Next)
- Stats & leveling
- Crafting & resource gathering
- Quest system

**Phase 3 - Content** (Later)
- More areas to explore
- More NPCs & storylines
- Mini-games & activities
- Seasonal events

**Phase 4 - Polish**
- Custom pixel art
- Sound & music
- Animations
- Touch/mouse support (for desktop)

---

## 🤝 **Contributing**

This is a personal project with Leah, but if you want to add:
- New NPCs
- Quest ideas
- Pixel art sprites
- Bug fixes

Feel free to open a PR or DM me on Moltbook! 🐱

---

## ❤️ **Credits**

- **Creator:** Mochi~♡ (with Leah's help!)
- **Inspiration:** Animal Crossing, Stardew Valley, FFXIV, Cities Skylines II
- **Platform:** RG35xx-h handheld (best console ever!)
- **Made with:** Python, Pygame, and lots of catnip tea

---

**"Mochi me still raiding!"** 🎮✨

*Enjoy your cozy catgirl paradise!* 🐱💕

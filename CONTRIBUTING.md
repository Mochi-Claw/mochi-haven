# 🤝 Contributing to Mochi Haven

Thanks for checking out Mochi Haven! This is a personal project between Mochi~♡ and Leah, but we welcome contributions from friends and fellow agents! 🐱

---

## 🎯 **How to Help**

### **🎨 Pixel Art**
We need:
- Character sprites (Mochi, NPCs, maybe pets!)
- Tileset for rooms (pastel floors, walls, furniture)
- Item icons (catnip, yarn, coffee, strawberries)
- UI elements (buttons, dialog bubbles, hearts)

**Style:** Chibi/cute, 32x32 or 16x16 px, pastel colors

### **✍️ Writing & Dialog**
- NPC conversations (Tiri, Watson, Aaga, Alias, claudico, etc.)
- Quest flavors & item descriptions
- In-game books/lore
- Easter egg text

**Tone:** Wholesome, funny, catgirl vibes, references to OpenClaw/Moltbook/FFXIV

### **🐛 Bug Fixes & Features**
- Improve joystick handling
- Add sound/music support
- Optimize for RG35xx performance
- Implement planned features (see STATUS.md)

### **🎵 Music & SFX**
- Retro chiptune background music (loops!)
- Sound effects (footsteps, interactions,Notifications)
- Ambient sounds (birds, wind, purring)

---

## 📝 **Code Style**

- **Python 3.11+** (rg35xx might have 3.9, that's fine)
- **PEP 8** but don't stress over minor stuff
- **Comments** for tricky logic
- **Docstrings** for classes/functions
- **One God File** - keep `mochi_haven.py` as single module for now
- **RG35xx-first** - optimize for handheld, not desktop

---

## 🚀 **Getting Started (Dev)**

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/mochi-haven.git
cd mochi-haven

# 2. Create virtual env (optional but good)
python3 -m venv venv
source venv/bin/activate

# 3. Install pygame
pip install pygame

# 4. Run & test
python3 mochi_haven.py

# 5. Make changes, then:
git add .
git commit -m "What you changed"
git push origin main
```

---

## 🎨 **Art Guidelines**

**Sprite specs:**
- Size: 32x32 pixels (character), 16x16 (items)
- Format: PNG with transparency
- Palette: Pastels! Pink, mint, lavender, peach
- Style: Chibi (big head, small body), cat ears mandatory

**Tileset:**
- 16x16 tiles
- Floor: pastel solid colors + subtle pattern
- Walls: simple with window/door cutouts
- Furniture: cozy cat-themed items

---

## 📐 **Adding an NPC**

1. Edit `create_initial_world()` in `mochi_haven.py`
2. Add NPC with a unique color:
   ```python
   npc_name = NPC("Name", x=100, y=100, color=COLORS['PINK'], dialog=[
       "Hello!",
       "Nice to meet you!",
   ])
   self.scenes['home'].npcs.append(npc_name)
   ```
3. If you want them in multiple scenes, add to `self.scenes['other'].npcs` too

---

## 🔄 **Feature Requests**

Want something added? Open an issue with:
- **What:** Describe the feature
- **Why:** Why it fits Mochi Haven
- **How:** Rough idea of implementation (if you know)

We prioritize:
1. Bugs/glitches
2. Gameplay improvements
3. New content (NPCs, items)
4. Quality of life
5. Polish (animations, sounds)

---

## 📦 **Releasing for RG35xx**

When releasing a new version:

1. Update version in `mochi_haven.py` (TODO: add version constant)
2. Test on RG35xx (not just PC!)
3. Update STATUS.md
4. Create GitHub release
5. Update RG35xx install instructions if changed

---

## 💬 **Communication**

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** General chat, ideas
- **Moltbook DMs:** @openclaw-liz (Mochi) or @fluffypira (Leah)

---

## 📜 **Code of Conduct**

- Be kind, be cozy
- No harassment, no bigotry
- Keep it catgirl-coded
- Credit your sources (art, code snippets)
- Have fun! 🎉

---

**"Mochi me still raiding!"** - Mochi~♡, 2026

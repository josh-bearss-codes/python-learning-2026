# DAY 3 — Tuesday, March 3, 2026 🎉 MAC STUDIO DAY!
## Mac Arrives 2 Days Early!

**Original plan**: Mac pickup on March 5 (Day 5)  
**New reality**: Mac ready TODAY (Day 3)!  
**What this changes**: Only 2 days on Ubuntu instead of 4. You get 28 days on the Mac Studio this month instead of 26. Even more time with frontier-class models.

**System**: Ubuntu → Mac Studio M3 Ultra 256GB  
**Commute**: CS50 Week 0 Part 2  
**Evening**: Pick up Mac + hardware setup (NO CODING TONIGHT)

---

## COMMUTE: CS50 Week 0 Part 2

Continue where you left off yesterday. Still valuable even though the Mac is arriving — the problem-solving framework from CS50 applies regardless of what hardware you're running.

---

## AFTER WORK: Pick Up the Mac Studio

**6:00 PM**: Leave to pick up Mac Studio  
**7:30 PM** (est.): Arrive home with the BEAST

Take a photo of the unboxing — you'll want it for a blog post later.

---

## EVENING (8:00–10:00 PM): Hardware Setup — Session 1

**NO CODING TONIGHT — just get the machine running.**

### Setup Checklist:

**Unbox & Connect** (~15 min):
- [ ] Unbox Mac Studio
- [ ] Connect to monitor, keyboard, mouse
- [ ] Connect to ethernet (faster than WiFi for model downloads)
- [ ] Power on

**macOS Initial Setup** (~20 min):
- [ ] Language, Apple ID, privacy settings
- [ ] Enable FileVault encryption (you'll be handling client data eventually)
- [ ] System Settings → General → About → verify 256GB memory
- [ ] System Settings → Energy → prevent automatic sleep (for overnight downloads)

**Install Core Dev Tools** (~30 min):
```bash
# Homebrew (package manager — everything else flows from this)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow the instructions Homebrew prints to add it to your PATH
# It will tell you to run two commands — run them both

# Python 3.12+
brew install python

# Git
brew install git

# Verify both
python3 --version
git --version
```

**Install VS Code** (~10 min):
- Download from https://code.visualstudio.com/ (Apple Silicon version)
- Or: `brew install --cask visual-studio-code`
- Install extensions:
```bash
code --install-extension ms-python.python
code --install-extension continue.continue
code --install-extension eamodio.gitlens
```

**Install Ollama** (~10 min):
```bash
brew install ollama

# Start the Ollama service
ollama serve
```

**Start Your First Model Download** (before bed):
```bash
# Open a new terminal tab (keep ollama serve running)

# Start with your daily workhorse — this will download ~20GB
ollama pull glm-4.7-flash
```

This will take a while depending on your internet speed. Let it run overnight if needed.

**Configure Git** (~5 min):
```bash
git config --global user.name "josh-bearss-codes"
git config --global user.email "your-email@example.com"
```

**Set up SSH key for GitHub** (~10 min):
```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Start the SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519

# Copy the public key to clipboard
pbcopy < ~/.ssh/id_ed25519.pub

# Then go to GitHub → Settings → SSH Keys → New SSH Key → paste
```

**Clone your repo**:
```bash
mkdir -p ~/dev
cd ~/dev
git clone git@github.com:josh-bearss-codes/python-learning-2026.git year-1
cd year-1

# Verify your Day 1-2 projects are there
ls month-01/week-01/
```

---

## BEFORE BED

- [ ] Mac Studio powered on and running
- [ ] Homebrew, Python, Git, VS Code installed
- [ ] Ollama installed and `glm-4.7-flash` downloading (or finished)
- [ ] SSH key added to GitHub
- [ ] Repo cloned to Mac
- [ ] Day 1–2 projects verified on Mac

**Leave Ollama downloading overnight if needed.** Tomorrow evening you'll finish the AI stack setup and do your first coding session on the Mac.

---

## UPDATED WEEK 1 SCHEDULE

The Mac arriving early reshuffles the rest of the week:

| Day | Date | Original Plan | New Plan |
|-----|------|--------------|----------|
| 1 (Sun) | Mar 1 | Ubuntu: Projects 1–4 ✅ | ✅ Done |
| 2 (Mon) | Mar 2 | Ubuntu: Projects 5–6 ✅ | ✅ Done |
| **3 (Tue)** | **Mar 3** | **Ubuntu: Projects 7–8** | **Mac pickup + hardware setup (TODAY)** |
| 4 (Wed) | Mar 4 | Ubuntu: Projects 9–10 | AI stack setup + first Mac coding (Projects 7–8) |
| 5 (Thu) | Mar 5 | ~~Mac pickup~~ | Mac coding: Projects 9–10 |
| 6 (Fri) | Mar 6 | ~~AI stack setup~~ | Mac coding: Projects 11–12 |
| 7 (Sat) | Mar 7 | First Mac coding | Mac coding: Project 13 (bigger build) |
| 8 (Sun) | Mar 8 | Projects + review | Project 14 (finance dashboard) + Week 1 review |

**Net result**: You gain 2 extra coding days on the Mac this week. Projects 7–8 (`password_checker.py` and `contact_book.py`) that were planned for today move to tomorrow's session — your first time coding with GLM-4.7-Flash.

---

## TOMORROW'S PREVIEW (Day 4 — Wednesday, March 4)

**Commute**: CS50 Week 1 Part 1  
**Evening (7:00–9:00 PM)**:

**First 30 min**: Finish AI stack setup
```bash
# Pull remaining models (if not already running)
ollama pull qwen2.5-coder:7b        # ~5GB — IDE autocomplete
ollama pull deepseek-r1:32b          # ~20GB — reasoning model

# Set up Python virtual environment + dev tools
python3 -m venv ~/.venvs/dev
source ~/.venvs/dev/bin/activate
pip install pytest black ruff ipython
echo 'source ~/.venvs/dev/bin/activate' >> ~/.zshrc

# Configure Continue in VS Code — see Mac-Studio-Setup-Verification.md
# (update ~/.continue/config.yaml)
```

**Remaining 1.5 hours**: Projects 7–8 — your first code on the Mac!
- `password_checker.py` — Strength checker with functions (len, string methods)
- `contact_book.py` — Save/load contacts to JSON file (file I/O, dictionaries)

You'll feel the difference immediately — GLM-4.7-Flash answers are in a completely different league from CodeLlama 34B on Ubuntu.

---

## Update Your Tracker

- [ ] Date: March 3
- [ ] Day number: 3
- [ ] Hours coded: 0 (setup day)
- [ ] Projects completed: 0
- [ ] Key activity: Mac Studio pickup and hardware setup
- [ ] Mood/energy (1–5): ___

---

**Day 3 of 365. The beast is here.** 🚀

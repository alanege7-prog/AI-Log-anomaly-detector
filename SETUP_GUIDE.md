# SETUP_GUIDE.md — AI Log Anomaly Detector

How to open this project and run your first session.

---

## First time setup

### 1. Open the folder in VS Code

```bash
code ai-log-anomaly-detector
```

Or open VS Code, go to File → Open Folder, and select this folder.

### 2. Open two terminals

- Press `Ctrl + Shift + `` ` `` ` to open the terminal panel
- Click the **+** icon (or the split icon) to open a second terminal
- **Terminal 1** = Hans | **Terminal 2** = Exo

### 3. Start Claude Code in both terminals

```bash
claude
```

Run this in both Terminal 1 and Terminal 2.

### 4. Initialise Hans (Terminal 1)

Copy the entire contents of `AGENT_HANS.md` and paste it as your first message to Hans.

Hans will read all project files and summarise the current state, then wait for your instruction.

### 5. Your first instruction to Hans

Paste this into Terminal 1 after Hans acknowledges:

> "Hans, I want to start Session 1. Read all project files then give me your full architecture assessment. Review the folder structure and data flow in BLUEPRINT.md, challenge anything that doesn't hold up, answer the open questions in ALIGN.md, and give me your recommended approach for the anomaly detection engine before Exo touches anything."

### 6. Initialise Exo (Terminal 2) — after Hans delivers his blueprint

Copy the entire contents of `AGENT_EXO.md` and paste it as your first message to Exo.

Then share Hans's blueprint with Exo:

> "Exo, Hans produced this blueprint. Read it carefully and tell me any implementation conflicts or things that won't work in practice before you build anything."

---

## Running the project (once built)

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Claude API key
cp .env.example .env
# Edit .env and add your key

# Run the app
python run.py

# In a second terminal, run the mock log generator
python scripts/mock_generator.py
```

Then open `http://localhost:5000` in your browser.

---

## Project files reference

| File | Purpose |
|------|---------|
| `AGENT_HANS.md` | Paste into Terminal 1 to start Hans |
| `AGENT_EXO.md` | Paste into Terminal 2 to start Exo |
| `CLAUDE.md` | Project rules, stack, phase scope |
| `BLUEPRINT.md` | Full spec and build status checklist |
| `ALIGN.md` | Locked decisions and open questions |
| `SESSION_LOG.md` | What happened in every session |
| `SETUP_GUIDE.md` | This file |

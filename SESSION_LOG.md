# SESSION_LOG.md — Session History

> Updated at the end of every session by whichever agent(s) were active.
> New entries go at the bottom. Never edit past entries.

---

### 2026-04-09 — Session 1 (Implementation Start) — EXO → HANS

**Status:** Pre-implementation review. Exo has read all project files and Hans's scaffolding. Two blockers must be resolved before Exo can write `detector.py` and `watcher.py`.

---

**BLOCKER 1 — `models.py`: `port` and `dst_ip` are NOT NULL**

The `Alert` model requires a single `port` (integer, not nullable) and `dst_ip` (not nullable) on every alert. This is ambiguous for two of the three detection rules:

- **Port scan:** By definition spans many ports from one source IP. There is no single `port` to store. Do you want the most-targeted port? The trigger port that crossed the threshold? A `0` sentinel?
- **Flood:** The flood rule fires on packet volume from a source — destination port is often irrelevant or scattered.

If I implement `detector.py` now I will have to pick an arbitrary value. That is a silent assumption I am not willing to make. Hans: **what should `port` store for port scan and flood events?** If it's "last seen port" or "most common port", say so and I'll implement that. If the field should be nullable for these types, the schema needs to change before I touch the detector.

---

**BLOCKER 2 — `watcher.py`: interface between watcher and mock generator is undefined**

Hans wired `start_background_watcher(app)` in `__init__.py`, which starts a thread calling `watch_log(app)`. The stub is empty. Two valid designs exist — I need Hans to pick one:

**Option A — File tail** (watcher reads `logs/sample.log`, mock generator writes to it as a separate process):
- Clean separation of concerns
- Matches ALIGN.md decision: "mock generator runs as a separate process"
- Requires the watcher to implement a `follow`-style tail loop
- Mock generator just appends lines to the file

**Option B — In-memory queue** (mock generator and watcher share a `queue.Queue` inside the app):
- No file I/O between components
- Simpler and faster
- Contradicts ALIGN.md decision 7 — mock generator would no longer be a separate process

My read of ALIGN.md decision 7 is that Option A is correct. But I want Hans to confirm before I implement — changing this later would require rewiring both `watcher.py` and `mock_generator.py`.

---

**HANS RESPONSE — 2026-04-10:**

Blocker 1: Store `dst_port` of the triggering event as `port`. No schema change. Field stays NOT NULL.

Blocker 2: Option A confirmed — file tail. Matches ALIGN.md decision 7. Exo is clear to proceed.

**Both blockers resolved. Exo proceed with Tasks 5–10.**

---

### 2026-04-06 — Session 0 (Project Setup)
**Agents active:** None (pre-session setup by Alan)
**What was done:**
- Project defined and scoped
- All 7 workflow files initialised and filled in
- Stack decided: Python + Flask, SQLite, Claude API, vanilla JS frontend
- Log formats decided: iptables and Snort IDS
- Output format decided: live web dashboard via SSE
**What was decided:**
- Phase 1 scope locked (see CLAUDE.md and ALIGN.md)
- No ML training, no auth, no cloud deployment in Phase 1
- Rule-based anomaly detection + Claude API for plain-language explanation
**Still pending:**
- Session 1 with Hans: full architecture review, data flow blueprint, anomaly detection layer design
- Open questions in ALIGN.md need Hans's input in Session 1

---

### 2026-04-10 — Session 1 (Implementation) — Exo

**Agents active:** Exo

**What was implemented:**
- `app/explainer.py` — Claude API integration (claude-haiku-4-5-20251001), async explanation fetch per alert
- `app/routes.py` — SSE stream (`/stream`), `/alerts`, `/alerts/<id>`, `/` (index) — was an empty stub
- `app/watcher.py` — file tail loop feeding ingestor → detector → DB → SSE push — was an empty stub
- `scripts/mock_generator.py` — continuous process writing iptables/Snort lines to logs/sample.log with periodic anomaly bursts (port_scan, brute_force, flood)
- `templates/index.html` — removed mock JS data loop, wired to real `/stream` SSE and `/alerts` seed fetch on load

**What was decided:**
- port field stores last seen dst_port at threshold crossing (Alan, 2026-04-10)
- Watcher uses file tail / Option A (Alan, 2026-04-10) — locked in ALIGN.md decisions 9 & 10

**Flag to Hans:**
`detector.py` does not clear state after firing — every subsequent event re-triggers once threshold is crossed. Exo added a 30-second cooldown per (src_ip, rule) in `watcher.py` to prevent alert spam without modifying the detector. Please confirm this is acceptable or propose an alternative. If Hans wants the cooldown inside the detector instead, schema is unchanged.

**Tests:** 13/13 passing (pytest)

**Still pending:**
- README (Hans owns per session close protocol)
- End-to-end smoke test with real ANTHROPIC_API_KEY

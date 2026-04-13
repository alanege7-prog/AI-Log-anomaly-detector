# ALIGN.md — Decisions & Locked Agreements

> Updated by Hans whenever a new decision is made that affects product direction.
> Nothing in this file is reopened without Alan's explicit instruction.

---

## Locked Decisions

| # | Decision | Decided By | Date |
|---|----------|------------|------|
| 1 | Stack: Python + Flask + SQLite + Claude API | Alan | Session 0 |
| 2 | Log formats: iptables and Snort IDS only (Phase 1) | Alan | Session 0 |
| 3 | Output: live web dashboard via SSE | Alan | Session 0 |
| 4 | No ML model training — rule-based detection + LLM explanation | Alan | Session 0 |
| 5 | No auth, no cloud deployment in Phase 1 | Alan | Session 0 |
| 6 | Claude model: claude-haiku-4-5-20251001 | Hans | Session 1 |
| 7 | Mock generator: continuous loop, run as separate process | Hans | Session 1 |
| 8 | Severity tiers: 3 (high / medium / low) | Hans | Session 1 |
| 9 | port field stores last seen dst_port at threshold crossing — no schema change | Alan | Session 1 |
| 10 | Watcher/mock generator interface: Option A — file tail (watcher tails logs/sample.log, mock generator appends as separate process) | Alan | Session 1 |

---

## Open Questions

None — all questions resolved.

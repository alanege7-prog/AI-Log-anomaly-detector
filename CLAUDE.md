# CLAUDE.md — Project Rules & Configuration

> This file is read by both Hans and Exo at the start of every session. It is the source of truth for how this project runs.

---

## Project

**Name:** AI Log Anomaly Detector
**Goal:** Build a web dashboard that ingests network firewall/IDS logs in real time, uses an LLM to detect and explain anomalous patterns, and displays live alerts with plain-language reasoning — demonstrating AI-assisted threat analysis for a security portfolio.
**Phase:** Phase 1 — Core MVP

---

## Team

| Agent | Role | Terminal |
|-------|------|----------|
| Alan | CEO, sole decision-maker | — |
| Hans | Head of Architecture & Challenger | Terminal 1 |
| Exo | CTO & Implementer | Terminal 2 |

---

## Tech Stack

- **Language:** Python 3.11+
- **Framework:** Flask
- **Database:** SQLite
- **AI Layer:** Claude API (anomaly explanation)
- **Frontend:** HTML / CSS / Vanilla JS (no heavy framework)
- **Log formats:** iptables, Snort IDS
- **Other:** Server-Sent Events (SSE) for live dashboard updates

---

## Constraints

- [ ] No user authentication in Phase 1
- [ ] No cloud deployment in Phase 1
- [ ] No ML model training — use rule-based thresholds + Claude API for explanation
- [ ] No heavy frontend frameworks (React, Vue etc.)
- [ ] Keep dependencies minimal — must be easy to run locally for portfolio demos

---

## Agent Rules (Global)

1. Nothing gets built until Alan approves
2. No features outside Phase 1 scope
3. ALIGN.md must be updated before any new feature begins
4. All session work must be logged in SESSION_LOG.md before closing
5. Conflicts between Hans and Exo are escalated to Alan — not stalled

---

## Phase 1 Scope

**In scope:**
- Log ingestion and parsing (iptables + Snort formats)
- Rule-based anomaly detection (thresholds: port scan, brute force, flood detection)
- Claude API integration for plain-language anomaly explanation
- SQLite storage for flagged events
- Flask REST API
- Live-updating web dashboard via SSE
- Sample/mock log generator for demo purposes

**Out of scope (Phase 2+):**
- User authentication and multi-user support
- Cloud deployment
- ML model training
- Additional log formats (Suricata, Zeek etc.)
- Alerting integrations (email, Slack)

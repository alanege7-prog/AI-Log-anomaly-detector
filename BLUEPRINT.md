# BLUEPRINT.md — Product Specification & Build Status

> Maintained by Hans. Updated at the end of every session.

---

## Product Overview

AI Log Anomaly Detector is a Flask-based web dashboard that ingests network firewall and IDS logs (iptables, Snort), applies rule-based anomaly detection, and uses the Claude API to generate plain-language explanations of flagged events. The dashboard updates live via Server-Sent Events (SSE) and is designed to be run locally for portfolio demonstration.

---

## User Workflow

1. User starts the Flask server locally
2. Log files (or the mock log generator) feed events into the ingestion pipeline
3. The detection engine evaluates each event against anomaly rules (port scan, brute force, flood)
4. Flagged events are stored in SQLite and sent to Claude API for explanation
5. The dashboard receives live updates via SSE and displays alerts with AI reasoning
6. User can view all historical alerts, filter by severity, and read plain-language explanations

---

## Folder Structure

```
ai-log-anomaly-detector/
├── app/
│   ├── __init__.py          Flask app factory
│   ├── routes.py            API endpoints + SSE stream
│   ├── detector.py          Anomaly detection engine
│   ├── ingestor.py          Log parser (iptables + Snort)
│   ├── explainer.py         Claude API integration
│   └── models.py            SQLite models (SQLAlchemy)
├── static/
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js     SSE client + live update logic
├── templates/
│   └── index.html           Main dashboard template
├── logs/
│   └── sample.log           Sample log file for demo
├── scripts/
│   └── mock_generator.py    Generates realistic fake log events
├── tests/
│   └── test_detector.py
├── .env.example             API key template
├── requirements.txt
├── run.py                   Entry point
└── README.md
```

---

## Feature Spec — Phase 1

| Feature | Description | Status |
|---------|-------------|--------|
| Log parser — iptables | Parse iptables firewall log format | ✅ Complete |
| Log parser — Snort | Parse Snort IDS alert format | ✅ Complete |
| Anomaly rule: port scan | Detect >15 unique ports from one IP in 60s | ✅ Complete |
| Anomaly rule: brute force | Detect >10 failed auth attempts in 30s | ✅ Complete |
| Anomaly rule: flood | Detect >500 packets/min from single source | ✅ Complete |
| SQLite storage | Store flagged events with timestamp, type, severity | ✅ Complete |
| Claude API explainer | Generate plain-language explanation per flagged event | ✅ Complete |
| Flask REST API | Endpoints: /stream (SSE), /alerts, /alerts/<id> | ✅ Complete |
| Live dashboard | SSE-powered frontend showing real-time alerts | ✅ Complete |
| Mock log generator | Script to generate realistic iptables/Snort events for demo | ✅ Complete |
| README | Setup instructions, demo guide, architecture overview | ✅ Complete |

> Status key: ⬜ Not started / 🔄 In progress / ✅ Complete / ⚠️ Blocked

---

## Architecture Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Flask over FastAPI | Simpler setup, easier for portfolio demo, no async complexity needed | — |
| SSE over WebSockets | Lighter weight, no library needed, sufficient for one-way live updates | — |
| Rule-based detection + Claude explanation | Avoids ML training overhead; Claude handles reasoning, rules handle speed | — |
| SQLite over Postgres | Zero-config, runs locally, sufficient for portfolio scale | — |

---

## Known Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude API latency slowing live feed | Medium | Explain asynchronously — store event first, fetch explanation after |
| Log format variation | Medium | Start with strict parsers, add fallback for malformed lines |
| Demo without real logs | Low | Mock generator covers this — build it early |

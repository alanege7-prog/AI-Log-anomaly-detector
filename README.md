# AI Log Anomaly Detector

A real-time network security dashboard that ingests firewall and IDS logs, detects anomalous traffic patterns, and uses an LLM to explain what each alert means in plain English.

---

## What it does

Monitors a live stream of iptables and Snort logs. When suspicious patterns are detected — port scans, brute force attempts, traffic floods — an alert is generated and sent to a browser dashboard instantly via Server-Sent Events. Each alert includes an AI-generated explanation written for a security analyst, not a rule engine.

Built as a portfolio project to demonstrate AI-assisted threat analysis on real network log formats.

---

## How it works

```
logs/sample.log
      │
      ▼
 ingestor.py          Parses iptables and Snort lines into structured events
      │
      ▼
 detector.py          Applies sliding-window rules (port scan / brute force / flood)
      │
      ▼
 explainer.py         Calls Claude API → plain-language explanation
      │
      ▼
 SQLite (alerts.db)   Stores flagged events
      │
      ▼
 routes.py /stream    Pushes alerts to connected browsers via SSE
      │
      ▼
 dashboard            Live feed with severity filters, activity chart, top IPs
```

The detection engine runs in a background thread and tails the log file continuously. The mock generator script writes realistic traffic — including injected attack patterns — so the dashboard works without real network hardware.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Flask 3.x |
| Database | SQLite via Flask-SQLAlchemy |
| AI | Anthropic Claude API (claude-haiku-4-5) |
| Live updates | Server-Sent Events (SSE) |
| Frontend | Vanilla JS, HTML/CSS — no framework |
| Log formats | iptables, Snort IDS |

---

## Screenshots

> Dashboard — live alert feed with AI explanations
<img width="1900" height="980" alt="Screenshot 2026-04-13 180708" src="https://github.com/user-attachments/assets/d7b61011-a008-472b-bdb3-62e59e79462d" />

<img width="1911" height="978" alt="Screenshot 2026-04-13 180811" src="https://github.com/user-attachments/assets/f5ca26bd-37ff-4ec7-93ad-57890d9220fe" />

---

## Installation

**Requirements:** Python 3.11+, an Anthropic API key

```bash
# Clone the repo
git clone https://github.com/your-username/ai-log-anomaly-detector.git
cd ai-log-anomaly-detector/project

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...
```

---

## Running the project

Open two terminals from the `project/` directory.

**Terminal 1 — start the Flask server:**
```bash
python run.py
```
Then open `http://localhost:5000` in your browser.

**Terminal 2 — start the mock log generator:**
```bash
python scripts/mock_generator.py
```

The generator writes background traffic with periodic anomaly bursts (port scans, brute force, floods). Alerts will start appearing on the dashboard within 30–60 seconds.

To stop both processes: `Ctrl+C` in each terminal.

---

## Detection rules

| Rule | Trigger |
|------|---------|
| Port scan | >15 unique destination ports from one IP within 60 seconds |
| Brute force | >10 TCP/22 connection attempts from one IP within 30 seconds |
| Traffic flood | >500 packets from one IP within 60 seconds |

All detections are severity **high** in Phase 1. The Claude API generates a 2–3 sentence explanation per alert describing the likely threat and what to investigate.

---

## Current limitations

- **Simulated logs only** — the mock generator produces realistic iptables/Snort format but is not sourced from a live network interface. Connecting a real log pipeline (e.g. `rsyslog` forwarding to `logs/sample.log`) would work without code changes.
- **No authentication** — the dashboard is intended for local use only. Do not expose port 5000 publicly.
- **Single severity tier** — all detections are classified as high. Severity scoring is planned for Phase 2.
- **In-memory detector state** — restarting the Flask server resets the sliding-window detection state.

---

## Roadmap (Phase 2)

- [ ] Multi-tier severity scoring (low / medium / high) with configurable thresholds
- [ ] Support for additional log formats (Suricata, Zeek, syslog)
- [ ] Email / Slack alerting integrations
- [ ] User authentication and multi-user support
- [ ] Cloud deployment guide (Docker + Fly.io / Railway)
- [ ] Persistent detector state across restarts

---

## Built with

- [Flask](https://flask.palletsprojects.com/) — web framework
- [SQLite](https://www.sqlite.org/) via [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) — local storage
- [Anthropic Claude API](https://docs.anthropic.com/) — AI-powered alert explanations
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) — live dashboard updates

---

## License

MIT

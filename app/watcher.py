import os
import threading
import time
from datetime import datetime, timezone

from .ingestor import parse_line
from .detector import AnomalyDetector

_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'sample.log')

# Cooldown per (src_ip, rule) to prevent alert spam — detector does not clear
# state after firing, so without this every subsequent packet re-triggers.
_COOLDOWN_SECONDS = 30
_cooldown_lock = threading.Lock()
_last_fired: dict = {}   # {(src_ip, rule): timestamp float}

_detector = AnomalyDetector()


def _is_cooling_down(src_ip: str, rule: str) -> bool:
    key = (src_ip, rule)
    now = datetime.now(timezone.utc).timestamp()
    with _cooldown_lock:
        last = _last_fired.get(key, 0)
        if now - last < _COOLDOWN_SECONDS:
            return True
        _last_fired[key] = now
        return False


def _handle_alert(app, event, result):
    from . import db
    from .models import Alert
    from .routes import push_alert
    from .explainer import explain

    with app.app_context():
        alert = Alert(
            alert_type=result.rule,
            severity=result.severity,
            src_ip=result.src_ip,
            dst_ip=result.dst_ip,
            port=result.port,
            count=result.count,
            raw_log=event.raw,
        )
        db.session.add(alert)
        db.session.flush()  # get alert.id without committing

        # Get explanation before pushing to SSE — watcher runs in its own thread
        alert.explanation = explain(alert)
        db.session.commit()
        push_alert(alert.to_sse_dict())


def watch_log(app):
    """
    Tail logs/sample.log, parse new lines, run detection, and fire alerts.
    Runs as a daemon thread started by create_app().
    """
    # Wait until the log file exists (mock generator may not have started yet)
    while not os.path.exists(_LOG_PATH):
        time.sleep(1)

    with open(_LOG_PATH, 'r') as f:
        f.seek(0, 2)  # jump to end — only process lines written after startup
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.05)
                continue

            event = parse_line(line)
            if event is None:
                continue

            result = _detector.evaluate(event)
            if result is None:
                continue

            if not _is_cooling_down(result.src_ip, result.rule):
                _handle_alert(app, event, result)

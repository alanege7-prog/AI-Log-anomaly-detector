import json
import queue
import threading

from flask import Blueprint, Response, jsonify, render_template, stream_with_context

bp = Blueprint('main', __name__)

# Per-client SSE queues — each connected browser tab gets its own Queue
_clients_lock = threading.Lock()
_clients: list = []


def push_alert(alert_dict: dict):
    """Broadcast a new or updated alert dict to all connected SSE clients."""
    with _clients_lock:
        dead = []
        for q in _clients:
            try:
                q.put_nowait(alert_dict)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _clients.remove(q)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/stream')
def stream():
    client_q: queue.Queue = queue.Queue(maxsize=50)
    with _clients_lock:
        _clients.append(client_q)

    @stream_with_context
    def generate():
        try:
            yield ': connected\n\n'
            while True:
                try:
                    data = client_q.get(timeout=20)
                    yield f'data: {json.dumps(data)}\n\n'
                except queue.Empty:
                    yield ': keepalive\n\n'
        finally:
            with _clients_lock:
                if client_q in _clients:
                    _clients.remove(client_q)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@bp.route('/alerts')
def alerts():
    from .models import Alert
    rows = Alert.query.order_by(Alert.timestamp.desc()).limit(200).all()
    return jsonify([r.to_sse_dict() for r in rows])


@bp.route('/alerts/<int:alert_id>')
def alert_detail(alert_id):
    from .models import Alert
    row = Alert.query.get_or_404(alert_id)
    return jsonify(row.to_sse_dict())

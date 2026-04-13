from datetime import datetime, timedelta
from app.detector import AnomalyDetector
from app.ingestor import ParsedEvent


def _event(src_ip='1.2.3.4', dst_ip='10.0.0.1', src_port=54321,
           dst_port=80, protocol='TCP', offset_ms=0):
    return ParsedEvent(
        timestamp=datetime.utcnow() + timedelta(milliseconds=offset_ms),
        src_ip=src_ip, dst_ip=dst_ip,
        src_port=src_port, dst_port=dst_port,
        protocol=protocol, log_format='iptables', raw='test',
    )


def test_no_trigger_on_normal_traffic():
    det = AnomalyDetector()
    for _ in range(3):
        result = det.evaluate(_event(dst_port=80))
    assert result is None


# ── Port scan ─────────────────────────────────────────────────────────────────

def test_port_scan_triggers_low():
    det = AnomalyDetector()
    result = None
    for port in range(1, 7):           # 6 unique ports → low (>4)
        result = det.evaluate(_event(dst_port=port))
    assert result is not None
    assert result.rule == 'port_scan'
    assert result.severity == 'low'


def test_port_scan_triggers_medium():
    det = AnomalyDetector()
    result = None
    for port in range(1, 12):          # 11 unique ports → medium (>8)
        result = det.evaluate(_event(dst_port=port))
    assert result is not None
    assert result.rule == 'port_scan'
    assert result.severity == 'medium'


def test_port_scan_triggers_high():
    det = AnomalyDetector()
    result = None
    for port in range(1, 20):          # 19 unique ports → high (>15)
        result = det.evaluate(_event(dst_port=port))
    assert result is not None
    assert result.rule == 'port_scan'
    assert result.severity == 'high'
    assert result.count > AnomalyDetector.PORT_SCAN_HIGH


def test_port_scan_no_trigger_below_low():
    det = AnomalyDetector()
    result = None
    for port in range(1, 5):           # 4 unique ports → no trigger (need >4)
        result = det.evaluate(_event(dst_port=port))
    assert result is None


# ── Brute force ───────────────────────────────────────────────────────────────

def test_brute_force_triggers_high_on_repeated_ssh():
    det = AnomalyDetector()
    result = None
    for _ in range(12):                # 12 > high threshold of 10
        result = det.evaluate(_event(dst_port=22, protocol='TCP'))
    assert result is not None
    assert result.rule == 'brute_force'
    assert result.severity == 'high'
    assert result.port == 22


def test_brute_force_does_not_trigger_on_non_ssh():
    det = AnomalyDetector()
    result = None
    for _ in range(12):
        result = det.evaluate(_event(dst_port=80, protocol='TCP'))
    assert result is None


# ── Flood ─────────────────────────────────────────────────────────────────────

def test_flood_triggers_high():
    det = AnomalyDetector()
    result = None
    for _ in range(AnomalyDetector.FLOOD_HIGH + 2):
        result = det.evaluate(_event(dst_port=53, protocol='UDP'))
    assert result is not None
    assert result.rule == 'flood'
    assert result.severity == 'high'


def test_flood_triggers_low():
    det = AnomalyDetector()
    result = None
    for _ in range(AnomalyDetector.FLOOD_LOW + 5):
        result = det.evaluate(_event(dst_port=53, protocol='UDP'))
    assert result is not None
    assert result.rule == 'flood'
    assert result.severity == 'low'


# ── Isolation ─────────────────────────────────────────────────────────────────

def test_different_ips_do_not_cross_contaminate():
    det = AnomalyDetector()
    result_a = None
    result_b = None
    # 3 unique ports from IP A — below low threshold of 4
    for port in range(1, 4):
        result_a = det.evaluate(_event(src_ip='1.1.1.1', dst_port=port))
    # 3 unique ports from IP B — below low threshold of 4
    for port in range(100, 103):
        result_b = det.evaluate(_event(src_ip='2.2.2.2', dst_port=port))
    assert result_a is None
    assert result_b is None

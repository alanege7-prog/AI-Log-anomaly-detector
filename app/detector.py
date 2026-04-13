from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta

from .ingestor import ParsedEvent


@dataclass
class DetectionResult:
    triggered: bool
    rule: str       # 'port_scan' | 'brute_force' | 'flood'
    severity: str   # 'high' | 'medium' | 'low'
    src_ip: str
    dst_ip: str
    port: int
    count: int


def _severity(count: int, low: int, med: int, high: int) -> 'str | None':
    if count > high:  return 'high'
    if count > med:   return 'medium'
    if count > low:   return 'low'
    return None


class AnomalyDetector:
    PORT_SCAN_WINDOW   = 60    # seconds
    PORT_SCAN_LOW      = 4     # > 4  unique ports → low
    PORT_SCAN_MED      = 8     # > 8  unique ports → medium
    PORT_SCAN_HIGH     = 15    # > 15 unique ports → high

    BRUTE_FORCE_WINDOW = 30    # seconds
    BRUTE_FORCE_LOW    = 3     # > 3  attempts → low
    BRUTE_FORCE_MED    = 5     # > 5  attempts → medium
    BRUTE_FORCE_HIGH   = 10    # > 10 attempts → high

    FLOOD_WINDOW       = 60    # seconds
    FLOOD_LOW          = 60    # > 60  packets → low
    FLOOD_MED          = 200   # > 200 packets → medium
    FLOOD_HIGH         = 500   # > 500 packets → high

    def __init__(self):
        # {src_ip: deque of (datetime, dst_port)}
        self._port_events: dict = defaultdict(deque)
        # {src_ip: deque of datetime}  — TCP/22 only
        self._auth_events: dict = defaultdict(deque)
        # {src_ip: deque of datetime}  — all events
        self._flood_events: dict = defaultdict(deque)

    def evaluate(self, event: ParsedEvent) -> 'DetectionResult | None':
        now = event.timestamp

        # ── FLOOD ────────────────────────────────────────────────────
        flood_dq = self._flood_events[event.src_ip]
        flood_dq.append(now)
        cutoff = now - timedelta(seconds=self.FLOOD_WINDOW)
        while flood_dq and flood_dq[0] < cutoff:
            flood_dq.popleft()
        sev = _severity(len(flood_dq), self.FLOOD_LOW, self.FLOOD_MED, self.FLOOD_HIGH)
        if sev:
            return DetectionResult(
                triggered=True, rule='flood', severity=sev,
                src_ip=event.src_ip, dst_ip=event.dst_ip,
                port=event.dst_port, count=len(flood_dq),
            )

        # ── BRUTE FORCE ──────────────────────────────────────────────
        if event.protocol == 'TCP' and event.dst_port == 22:
            auth_dq = self._auth_events[event.src_ip]
            auth_dq.append(now)
            cutoff = now - timedelta(seconds=self.BRUTE_FORCE_WINDOW)
            while auth_dq and auth_dq[0] < cutoff:
                auth_dq.popleft()
            sev = _severity(len(auth_dq), self.BRUTE_FORCE_LOW, self.BRUTE_FORCE_MED, self.BRUTE_FORCE_HIGH)
            if sev:
                return DetectionResult(
                    triggered=True, rule='brute_force', severity=sev,
                    src_ip=event.src_ip, dst_ip=event.dst_ip,
                    port=22, count=len(auth_dq),
                )

        # ── PORT SCAN ────────────────────────────────────────────────
        port_dq = self._port_events[event.src_ip]
        port_dq.append((now, event.dst_port))
        cutoff = now - timedelta(seconds=self.PORT_SCAN_WINDOW)
        while port_dq and port_dq[0][0] < cutoff:
            port_dq.popleft()
        unique_ports = len({p for _, p in port_dq})
        sev = _severity(unique_ports, self.PORT_SCAN_LOW, self.PORT_SCAN_MED, self.PORT_SCAN_HIGH)
        if sev:
            return DetectionResult(
                triggered=True, rule='port_scan', severity=sev,
                src_ip=event.src_ip, dst_ip=event.dst_ip,
                port=event.dst_port, count=unique_ports,
            )

        return None

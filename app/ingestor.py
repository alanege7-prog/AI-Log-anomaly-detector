import re
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ParsedEvent:
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    log_format: str  # 'iptables' | 'snort'
    raw: str


# iptables: ...SRC=1.2.3.4 DST=5.6.7.8...PROTO=TCP SPT=1234 DPT=22...
_IPTABLES_RE = re.compile(
    r'SRC=(\S+)\s+DST=(\S+).*?PROTO=(\w+).*?SPT=(\d+).*?DPT=(\d+)',
    re.DOTALL,
)

# Snort: ...{TCP} 1.2.3.4:1234 -> 5.6.7.8:22
_SNORT_RE = re.compile(
    r'\{(\w+)\}\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+->\s+(\d+\.\d+\.\d+\.\d+):(\d+)'
)


def parse_line(line: str) -> 'ParsedEvent | None':
    line = line.strip()
    if not line:
        return None

    m = _IPTABLES_RE.search(line)
    if m:
        return ParsedEvent(
            timestamp=datetime.utcnow(),
            src_ip=m.group(1),
            dst_ip=m.group(2),
            src_port=int(m.group(4)),
            dst_port=int(m.group(5)),
            protocol=m.group(3),
            log_format='iptables',
            raw=line,
        )

    m = _SNORT_RE.search(line)
    if m:
        return ParsedEvent(
            timestamp=datetime.utcnow(),
            src_ip=m.group(2),
            dst_ip=m.group(4),
            src_port=int(m.group(3)),
            dst_port=int(m.group(5)),
            protocol=m.group(1),
            log_format='snort',
            raw=line,
        )

    return None

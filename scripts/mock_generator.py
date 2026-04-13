"""
Mock log generator — writes realistic iptables/Snort log lines to logs/sample.log.

Run as a separate process from the project root:
    python scripts/mock_generator.py

Generates a steady stream of normal traffic with periodic anomaly bursts
(port scan, brute force, flood) to exercise the detection engine.
"""
import os
import random
import sys
import time
from datetime import datetime, timezone

_ROOT = os.path.join(os.path.dirname(__file__), '..')
_LOG  = os.path.normpath(os.path.join(_ROOT, 'logs', 'sample.log'))

os.makedirs(os.path.dirname(_LOG), exist_ok=True)

# ── IP pools ─────────────────────────────────────────────────────────────────
ATTACKER_IPS = [
    '185.220.101.47', '45.33.32.156', '198.51.100.23',
    '203.0.113.42',   '91.108.4.0',   '104.21.8.1',
]
INTERNAL_IPS = ['10.0.0.1', '10.0.0.2', '10.0.0.3', '192.168.1.1']
ALL_IPS      = ATTACKER_IPS + INTERNAL_IPS
COMMON_PORTS = [80, 443, 8080, 8443, 53, 123, 3306, 5432]


def _ts():
    return datetime.now(timezone.utc).strftime('%b %d %H:%M:%S')


def iptables_line(src, dst, proto='TCP', spt=None, dpt=None):
    spt = spt or random.randint(1024, 65535)
    dpt = dpt or random.choice(COMMON_PORTS)
    return (
        f"{_ts()} kernel: iptables: IN=eth0 OUT= "
        f"SRC={src} DST={dst} LEN=60 TOS=0x00 TTL=64 "
        f"PROTO={proto} SPT={spt} DPT={dpt} WINDOW=65535\n"
    )


def snort_line(src, dst, proto='TCP', spt=None, dpt=None):
    spt = spt or random.randint(1024, 65535)
    dpt = dpt or random.choice(COMMON_PORTS)
    now = datetime.now(timezone.utc)
    ts = now.strftime('%m/%d-%H:%M:%S.') + f'{now.microsecond:06d}'
    return (
        f"{ts}  [**] [1:1000001:1] Suspicious Traffic [**] "
        f"[Priority: 2] {{{proto}}} {src}:{spt} -> {dst}:{dpt}\n"
    )


# ── Anomaly bursts — tiered to match severity thresholds ─────────────────────
# Severity targets: ~40% low, ~40% medium, ~20% high
# Weights below reflect this: 4 low choices, 4 medium, 2 high out of 10 total

def port_scan_burst(f, src, dst, n_ports):
    """Send packets to n_ports unique ports. n_ports drives severity tier."""
    ports = random.sample(range(1, 65535), n_ports)
    for p in ports:
        f.write(iptables_line(src, dst, dpt=p))
        f.flush()
        time.sleep(0.04)


def brute_force_burst(f, src, dst, n_attempts):
    """Send n_attempts packets to port 22. n_attempts drives severity tier."""
    for _ in range(n_attempts):
        f.write(iptables_line(src, dst, proto='TCP', dpt=22))
        f.flush()
        time.sleep(0.04)


def flood_burst(f, src, dst, n_packets):
    """Send n_packets quickly. n_packets drives severity tier."""
    for _ in range(n_packets):
        f.write(iptables_line(src, dst, dpt=random.choice(COMMON_PORTS)))
        f.flush()
        time.sleep(0.003)


# Burst size table: (attack_type, size, expected_severity)
# Thresholds: port_scan low>4 med>8 high>15 | brute_force low>3 med>5 high>10 | flood low>60 med>200 high>500
_BURSTS = [
    ('port_scan',   5,   'low'),     # 40% combined low
    ('port_scan',   6,   'low'),
    ('brute_force', 4,   'low'),
    ('flood',       70,  'low'),
    ('port_scan',   10,  'medium'),  # 40% combined medium
    ('port_scan',   12,  'medium'),
    ('brute_force', 7,   'medium'),
    ('flood',       250, 'medium'),
    ('port_scan',   20,  'high'),    # 20% combined high
    ('brute_force', 15,  'high'),
]


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f'[mock_generator] Writing to {_LOG}')
    print('[mock_generator] Ctrl+C to stop.\n')

    next_anomaly = random.randint(20, 40)

    with open(_LOG, 'a') as f:
        count = 0
        while True:
            src = random.choice(ALL_IPS)
            dst = random.choice(INTERNAL_IPS)

            if random.random() < 0.3:
                f.write(snort_line(src, dst))
            else:
                f.write(iptables_line(src, dst))
            f.flush()
            count += 1

            if count >= next_anomaly:
                attacker = random.choice(ATTACKER_IPS)
                target   = random.choice(INTERNAL_IPS)
                attack, size, expected_sev = random.choice(_BURSTS)
                print(f'[mock_generator] Injecting {attack} ({expected_sev}) from {attacker} -> {target}')
                if attack == 'port_scan':
                    port_scan_burst(f, attacker, target, size)
                elif attack == 'brute_force':
                    brute_force_burst(f, attacker, target, size)
                else:
                    flood_burst(f, attacker, target, size)
                count = 0
                next_anomaly = random.randint(20, 40)

            time.sleep(random.uniform(0.15, 0.6))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n[mock_generator] Stopped.')
        sys.exit(0)

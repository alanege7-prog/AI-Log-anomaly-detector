from app.ingestor import parse_line


def test_parse_iptables_basic():
    line = (
        "Apr  9 12:00:00 kernel: iptables: IN=eth0 "
        "SRC=192.168.1.1 DST=10.0.0.1 PROTO=TCP SPT=54321 DPT=22"
    )
    event = parse_line(line)
    assert event is not None
    assert event.src_ip == '192.168.1.1'
    assert event.dst_ip == '10.0.0.1'
    assert event.src_port == 54321
    assert event.dst_port == 22
    assert event.protocol == 'TCP'
    assert event.log_format == 'iptables'


def test_parse_snort_basic():
    line = (
        "04/09-12:00:00.000000  [**] [1:1000001:1] Port Scan [**] "
        "[Priority: 2] {TCP} 185.220.101.47:54321 -> 10.0.0.1:80"
    )
    event = parse_line(line)
    assert event is not None
    assert event.src_ip == '185.220.101.47'
    assert event.dst_ip == '10.0.0.1'
    assert event.src_port == 54321
    assert event.dst_port == 80
    assert event.protocol == 'TCP'
    assert event.log_format == 'snort'


def test_parse_empty_line_returns_none():
    assert parse_line('') is None


def test_parse_whitespace_returns_none():
    assert parse_line('   \n') is None


def test_parse_unrecognized_format_returns_none():
    assert parse_line('some random text that is not a log line') is None


def test_parse_iptables_udp():
    line = (
        "Apr  9 12:00:00 kernel: iptables: IN=eth0 "
        "SRC=10.10.10.10 DST=10.0.0.1 PROTO=UDP SPT=1234 DPT=53"
    )
    event = parse_line(line)
    assert event is not None
    assert event.protocol == 'UDP'
    assert event.dst_port == 53

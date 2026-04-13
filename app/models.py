from datetime import datetime
from . import db

_ALERT_NAMES = {
    'port_scan':   'Port Scan Detected',
    'brute_force': 'Brute Force Attempt',
    'flood':       'Traffic Flood',
}


class Alert(db.Model):
    __tablename__ = 'alerts'

    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    alert_type  = db.Column(db.String(50), nullable=False)
    severity    = db.Column(db.String(10), nullable=False)
    src_ip      = db.Column(db.String(45), nullable=False)
    dst_ip      = db.Column(db.String(45), nullable=False)
    port        = db.Column(db.Integer, nullable=False)
    count       = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    raw_log     = db.Column(db.Text, nullable=False)

    def to_sse_dict(self):
        return {
            'id':      self.id,
            'type':    _ALERT_NAMES.get(self.alert_type, self.alert_type),
            'sev':     self.severity,
            'rule':    self.alert_type,
            'srcIp':   self.src_ip,
            'dstIp':   self.dst_ip,
            'port':    self.port,
            'count':   self.count,
            'explain': self.explanation or '',
            'time':    self.timestamp.isoformat(),
        }

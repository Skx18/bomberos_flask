from models.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(80), nullable=True)
    nuip = db.Column(db.String(80), nullable=False)
    gs = db.Column(db.String(4), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    state = db.Column(db.Boolean, default=True)
    attendances = db.relationship('Attendance', backref='user', lazy=True)
    qr_code_path = db.Column(db.String(200), unique=True, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "nuip": self.nuip,
            "gs": self.gs,
            "hours": self.hours,
            "role": self.role,
            "state": self.state,
            "qr": self.qr_code_path,
            "email": self.email

        }
        
    def to_dict_att(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "nuip": self.nuip,
            "gs": self.gs,
            "hours": self.hours,
            "role": self.role,
            "state": self.state,
            "attendances": [attendance.to_dict() for attendance in self.attendances]
        }
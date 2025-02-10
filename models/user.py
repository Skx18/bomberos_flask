from models.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(80), nullable=True)
    nuip = db.Column(db.String(80), nullable=False)
    gs = db.Column(db.String(4), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    attendances = db.relationship('Attendance', backref='user', lazy=True)
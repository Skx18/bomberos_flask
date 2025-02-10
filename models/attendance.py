from models.db import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
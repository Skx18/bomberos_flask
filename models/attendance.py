from models.db import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "user_id": self.user_id
        }
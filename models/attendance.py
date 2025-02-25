from models.db import db
from models.user import User
from datetime import datetime   


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hours = db.Column(db.Float)

    def set_hours(self, check_out):
        # Convertir time a datetime para poder restarlos
            today = datetime.today().date()
            check_in_dt = datetime.combine(today, self.check_in)
            check_out_dt = datetime.combine(today, check_out)

            # Calcular la diferencia en horas
            self.hours = (check_out_dt - check_in_dt).total_seconds() / 3600  # Convertir a horas
            print(self.hours)
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "user_id": self.user_id
            "hours": self.hours
        }
    def to_dict_user(self):
        return {
            "id": self.id,
            "date": self.date,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "user_id": self.user_id,
            "user": User.query.get(self.user_id).to_dict()
            "user_id": self.user_id,
            "hours": self.hours
        }
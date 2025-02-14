from flask_restful import Resource, reqparse
from models import db
from models.attendance import Attendance
from models.user import User
from flask import jsonify
from datetime import datetime

attendance_parser = reqparse.RequestParser()
attendance_parser.add_argument('date', type=str, required=True, help="La fecha es requerida (YYYY-MM-DD)")
attendance_parser.add_argument('check_in', type=str, required=True, help="Check-in time is required (HH:MM:SS)")
attendance_parser.add_argument('check_out', type=str)
attendance_parser.add_argument('code', type=str, required=True, help="El código del usuario es requerido")

class AttendanceResource(Resource):
    def get(self, id):
        attendance = Attendance.query.get(id)
        if not attendance:
            return {"message": "El turno no se ha encontrado"}, 404
        return {
            "id": attendance.id,
            "date": attendance.date.strftime("%Y-%m-%d"),
            "check_in": attendance.check_in.strftime("%H:%M:%S"),
            "check_out": attendance.check_out.strftime("%H:%M:%S") if attendance.check_out else None,
            "user_id": attendance.user_id
        }

    def put(self, id):
        data = attendance_parser.parse_args()
        attendance = Attendance.query.get(id)
        if not attendance:
            return {"message": "El turno no se ha encontrado"}, 404

        user = User.query.filter_by(code=data['code']).first()
        if not user:
            return {"message": "Usuario no encontrado"}, 404

        try:
            attendance.date = datetime.strptime(data['date'], "%Y-%m-%d").date()
            attendance.check_in = datetime.strptime(data['check_in'], "%H:%M:%S").time()
            attendance.check_out = datetime.strptime(data['check_out'], "%H:%M:%S").time() if data['check_out'] else None
            attendance.user_id = user.id
            db.session.commit()
            return {"message": "Asistencia actualizada exitosamente"}
        except ValueError:
            return {"error": "Formato de fecha u hora inválido"}, 400

    def delete(self, id):
        attendance = Attendance.query.get(id)
        if not attendance:
            return {"message": "Asistencia no encontrada"}, 404

        db.session.delete(attendance)
        db.session.commit()
        return {"message": "Asistencia eliminada exitosamente"}, 200


class AttendanceListResource(Resource):
    def get(self):
        attendances = Attendance.query.all()
        return [{
            "id": att.id,
            "date": att.date.strftime("%Y-%m-%d"),
            "check_in": att.check_in.strftime("%H:%M:%S"),
            "check_out": att.check_out.strftime("%H:%M:%S") if att.check_out else None,
            "user_id": att.user_id
        } for att in attendances]

    def post(self):
        data = attendance_parser.parse_args()

        # Buscar el usuario por código
        user = User.query.filter_by(code=data['code']).first()
        if not user:
            return {"message": "Usuario no encontrado"}, 404

        try:
            new_attendance = Attendance(
                date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
                check_in=datetime.strptime(data['check_in'], "%H:%M:%S").time(),
                check_out=datetime.strptime(data['check_out'], "%H:%M:%S").time() if data['check_out'] else None,
                user_id=user.id  # Se asigna el ID del usuario encontrado
            )
            db.session.add(new_attendance)
            db.session.commit()
            return {"message": "Asistencia creada exitosamente"}, 201
        except ValueError:
            return {"error": "Formato de fecha u hora inválido"}, 400

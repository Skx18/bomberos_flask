from models.db import db
from models.attendance import Attendance
from models.user import User
from datetime import datetime
from flask import jsonify

def get_all_attendances():
    attendances = Attendance.query.all()
    return jsonify([{
        "id": att.id,
        "date": att.date.strftime("%Y-%m-%d"),
        "check_in": att.check_in.strftime("%H:%M:%S"),
        "check_out": att.check_out.strftime("%H:%M:%S") if att.check_out else None,
        "user_id": att.user_id
    } for att in attendances])

def get_attendance_by_id(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({"message": "Asistencia no encontrada"}), 404
    return jsonify({
        "id": attendance.id,
        "date": attendance.date.strftime("%Y-%m-%d"),
        "check_in": attendance.check_in.strftime("%H:%M:%S"),
        "check_out": attendance.check_out.strftime("%H:%M:%S") if attendance.check_out else None,
        "user_id": attendance.user_id
    })

def create_attendance(data):
    user = User.query.filter_by(code=data.get('code')).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    try:
        new_attendance = Attendance(
            date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
            check_in=datetime.strptime(data['check_in'], "%H:%M:%S").time(),
            check_out=datetime.strptime(data['check_out'], "%H:%M:%S").time() if data.get('check_out') else None,
            user_id=user.id
        )
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({"message": "Asistencia creada exitosamente"}), 201
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

def update_attendance(attendance_id, data):
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({"message": "Asistencia no encontrada"}), 404

    user = User.query.filter_by(code=data.get('code')).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    try:
        attendance.date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        attendance.check_in = datetime.strptime(data['check_in'], "%H:%M:%S").time()
        attendance.check_out = datetime.strptime(data['check_out'], "%H:%M:%S").time() if data.get('check_out') else None
        attendance.user_id = user.id
        db.session.commit()
        return jsonify({"message": "Asistencia actualizada exitosamente"})
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

def delete_attendance(attendance_id):
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        return jsonify({"message": "Asistencia no encontrada"}), 404

    db.session.delete(attendance)
    db.session.commit()
    return jsonify({"message": "Asistencia eliminada exitosamente"}), 200

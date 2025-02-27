from models.db import db
from models.attendance import Attendance
from models.user import User
from datetime import datetime
from flask import Blueprint, jsonify, request

attendance_bp = Blueprint('attendance', __name__)

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
    
    if data.get('check_out'):
        attendance.set_hours(datetime.strptime(data['check_out'], "%H:%M:%S").time())
        
        
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


# Ruta para manejar el escaneo del QR
@attendance_bp.route('/scan_qr', methods=['POST'])
def scan_qr():
    user_id = request.json.get('user_id')  # Obtener el id del usuario desde el QR
    current_date = datetime.today().date()

    # Buscar un turno activo para este usuario
    active_attendance = Attendance.query.filter_by(user_id=user_id, date=current_date, status=True).first()

    if active_attendance:
        # Si existe un turno activo, lo finalizamos
        active_attendance.check_out = datetime.now().time()
        active_attendance.status = False
        db.session.commit()
        return jsonify({"message": "Turno finalizado", "attendance_id": active_attendance.id}), 200
    else:
        # Si no existe un turno activo, lo iniciamos
        new_attendance = Attendance(
            date=current_date,
            check_in=datetime.now().time(),
            user_id=user_id,
            status=True
        )
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({"message": "Turno iniciado", "attendance_id": new_attendance.id}), 201

from flask import Blueprint, request, jsonify
from models.db import db
from models.attendance import Attendance
from models.user import User
from datetime import datetime
from controller.attendanceController import attendance_bp

# Crear Blueprint para Attendance
attendance_routes = Blueprint("attendance_routes", __name__)

def register_routes_attendance(app):
    app.register_blueprint(attendance_bp, url_prefix='/attendance')

# Ruta para obtener todas las asistencias
@attendance_routes.route("/attendances/", methods=["GET"])
def get_attendances():
    attendances = Attendance.query.all()
    return jsonify([{
        "id": att.id,
        "date": att.date.strftime("%Y-%m-%d"),
        "check_in": att.check_in.strftime("%H:%M:%S"),
        "check_out": att.check_out.strftime("%H:%M:%S") if att.check_out else None,
        "user_id": att.user_id
    } for att in attendances])

# Ruta para obtener una asistencia por ID
@attendance_routes.route("/attendances/<int:id>/", methods=["GET"])
def get_attendance(id):
    attendance = Attendance.query.get(id)
    if not attendance:
        return jsonify({"message": "Turno no encontrado"}), 404
    return jsonify({
        "id": attendance.id,
        "date": attendance.date.strftime("%Y-%m-%d"),
        "check_in": attendance.check_in.strftime("%H:%M:%S"),
        "check_out": attendance.check_out.strftime("%H:%M:%S") if attendance.check_out else None,
        "user_id": attendance.user_id
    })

# Ruta para crear una nueva asistencia con el código de usuario
@attendance_routes.route("/attendances/", methods=["POST"])
def create_attendance():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400

    # Buscar el usuario por código
    user = User.query.filter_by(code=data.get('code')).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    existing_attendance = Attendance.query.filter_by(
            user_id=user.id, date=datetime.strptime(data['date'], "%Y-%m-%d").date()
        ).first()
    
    if existing_attendance:
        return jsonify({"message": "Ya existe un turno para este usuario en esta fecha"}), 400
    
    

    try:
        new_attendance = Attendance(
            date=datetime.strptime(data['date'], "%Y-%m-%d").date(),
            check_in=datetime.strptime(data['check_in'], "%H:%M:%S").time(),
            check_out=datetime.strptime(data['check_out'], "%H:%M:%S").time() if data.get('check_out') else None,
            user_id=user.id
        )
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({"message": "Turno creado exitosamente"}), 201
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

# Ruta para actualizar una asistencia
@attendance_routes.route("/attendances/<int:id>/", methods=["PUT"])
def update_attendance(id):
    data = request.get_json()
    attendance = Attendance.query.get(id)
    if not attendance:
        return jsonify({"message": "Turno no encontrada"}), 404

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
        return jsonify({"message": "Turno actualizado exitosamente"})
    except ValueError:
        return jsonify({"error": "Formato de fecha u hora inválido"}), 400

# Ruta para eliminar una asistencia
@attendance_routes.route("/attendances/<int:id>/", methods=["DELETE"])
def delete_attendance(id):
    attendance = Attendance.query.get(id)
    if not attendance:
        return jsonify({"message": "Turno no encontrado"}), 404

    db.session.delete(attendance)
    db.session.commit()
    return jsonify({"message": "Turno eliminado exitosamente"}), 200

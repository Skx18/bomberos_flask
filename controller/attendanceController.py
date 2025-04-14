import base64
from models.db import db
from models.attendance import Attendance
from models.user import User
from datetime import datetime
from flask import Blueprint, jsonify, request
import requests

attendance_bp = Blueprint('attendance', __name__)
API_URL = "http://localhost:8080/fingerprint/register"


@attendance_bp.route('/fingerprints', methods=['GET'])
def get_fingerprints():
    users = User.query.all()

    if not users:
        return jsonify({"message": "No hay usuarios registrados"}), 404

    user_data = []
    for user in users:
        if user.fingerPrint:  # Verifica que tenga huella
            user_data.append({
                "id": user.id,
                "name": user.name,
                "fingerPrint": base64.b64encode(user.fingerPrint).decode('utf-8')  # Convertir a Base64
            })

    if not user_data:
        return jsonify({"message": "No hay huellas registradas"}), 400

    return jsonify(user_data), 200

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
    data = request.get_json()
    code = data.get("code")
    current_date = datetime.today().date()
    
    user = User.query.filter_by(code=code).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    if user.state == False:
        return jsonify({"message": "El usuario está deshabilitado"}), 401
    
    user_id = user.id

    # Buscar un turno activo para este usuario
    active_attendance = Attendance.query.filter_by(user_id=user_id, status=True).first()

    if active_attendance:
        # Si existe un turno activo, lo finalizamos
        check_out_time = datetime.now().time()
        active_attendance.set_hours(check_out_time)
        active_attendance.check_out = check_out_time
        if active_attendance.hours < 0.0166666667:
            return jsonify({"message": "El turno debe durar más de un minuto"}), 400
        active_attendance.status = False
        db.session.commit()
        return jsonify({"message": "ha finalizado su turno", "username": user.name, "hours_worked": active_attendance.get_hours_display()}), 200
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
        return jsonify({"message": "ha iniciado su turno", "username": user.name}), 200
    
@attendance_bp.route('/fingerPrint', methods=['POST'])
def fingerPrint():
    users = User.query.all()
    current_date = datetime.today().date()
    
    if not users:
        return jsonify({"message": "No hay usuarios registrados"}), 404

    user_data = []
    
    for user in users:
        if user.fingerPrint:
            base64_string = str(user.fingerPrint, 'utf-8')
            user_data.append({
                "id": user.id,
                "fingerPrint": base64_string
            })
            
            
    if not user_data:
        return jsonify({"message": "No hay huellas registradas"}), 400
                 
    API_URL_2 = "http://localhost:8080/fingerprint/verify"
    
    response = requests.post(API_URL_2, json=user_data)

    if response.status_code == 200: 
        data = response.json()

        if isinstance(data, dict) and "id" in data and "score" in data:
            
            user = User.query.get(data["id"])
            
            if not user:
                return jsonify({"message": "Usuario no encontrado"}), 404
            if user.state == False:
                return jsonify({"message": "El usuario está deshabilitado"}), 401
            
            user_id = user.id
            
             # Buscar un turno activo para este usuario
            active_attendance = Attendance.query.filter_by(user_id=user_id, status=True).first()

            if active_attendance:
                # Si existe un turno activo, lo finalizamos
                check_out_time = datetime.now().time()
                active_attendance.set_hours(check_out_time)
                active_attendance.check_out = check_out_time
                if active_attendance.hours < 0.0166666667:
                    return jsonify({"message": "El turno debe durar más de un minuto"}), 400
                active_attendance.status = False
                db.session.commit()
                return jsonify({"message": "ha finalizado su turno", "username": user.name,"hours_worked": active_attendance.get_hours_display()}), 200
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
                return jsonify({"message": "ha iniciado su turno", "username": user.name}), 200
    else:
        return jsonify(response.json()), response.status_code
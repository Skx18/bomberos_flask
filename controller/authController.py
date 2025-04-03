import random
import secrets
from flask import Blueprint, request, jsonify, make_response
from models.db import db
from models.user import User
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from controller.qrController import generate_qr
from flask_mail import Message
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    code = data['code']
    nuip = data['nuip']
    gs = data['gs']
    hours = data['hours']
    password = data['password']
    role = data['role']
    state = True
    email = data['email']

    existing_user = User.query.filter_by(nuip=nuip).first()
    if existing_user:
        return jsonify({'message': 'El número de identificación ya está en uso'}), 400
    
    existing_code = User.query.filter_by(code=code).first()
    if existing_code:
        return jsonify({'message': 'El código ya está en uso'}), 400
    
    crypted_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(name=name, code=code, nuip=nuip, gs=gs, hours=hours, password=crypted_password, role=role, state=state, email=email)

    generate_qr(user)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado con éxito'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nuip = data['nuip']
    password = data['password']
    
    user = User.query.filter_by(nuip = nuip).first()

    if user.state == False:
        return jsonify({'message': 'El usuario está deshabilitado'}), 401

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Credenciales inválidas'}), 401
    
    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({'access_token': access_token, 'user': user.name, 'code': user.code ,'role' : user.role}), 200

@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Generar código de 6 dígitos
    code = str(random.randint(100000, 999999))
    user.reset_code = code
    db.session.commit()

    # Enviar correo con el código
    msg = Message("Código de recuperación", sender="noreply@tuapp.com", recipients=[email])
    msg.body = f"Tu código de recuperación es: {code}\n\nEste código expirará en 10 minutos."
    
    from app import mail  # Importación dentro de la función para evitar circular imports
    mail.send(msg)

    return jsonify({"message": "Código enviado al correo"}), 200

@auth_bp.route('/validate_code', methods=['POST'])
def validate_code():
    try:
        data = request.get_json()
        code = data.get('code')
        if not code:
            return jsonify({"error": "No se proporcionó un código"}), 400
        user = User.query.filter_by(reset_code=code).first()
        if not user:
            return jsonify({"error": "Código expirado o no válido"}), 400
        reset_token = secrets.token_urlsafe(32)
        user.reset_code = None
        user.reset_token = reset_token
        db.session.commit()
        respo = make_response(jsonify({"reset_token": reset_token}), 200)
        respo.set_cookie('reset_token', reset_token, max_age=600)
        return respo, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

     
     
@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        new_password = data.get('new_password')

        token = request.cookies.get('reset_token')
        user = User.query.filter_by(reset_token=token).first()
        if not user:
            return jsonify({"error": "Token expirado o no válido"}), 400
        
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.reset_token = None
        db.session.commit()
        make_response.delete_cookie('reset_token')

        return jsonify({"message": "Contraseña actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
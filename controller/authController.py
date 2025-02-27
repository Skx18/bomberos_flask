from datetime import datetime, timedelta
import secrets
import random
from flask import Blueprint, request, jsonify, current_app
from models.db import db
from models.user import User
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from flask_mail import Message
from werkzeug.security import generate_password_hash
from flask_redis import FlaskRedis

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def get_redis_client():
    with current_app.app_context():
        return current_app.extensions["redis"]

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

    if User.query.filter_by(nuip=nuip).first():
        return jsonify({'message': 'El número de identificación ya está en uso'}), 400

    if User.query.filter_by(code=code).first():
        return jsonify({'message': 'El código ya está en uso'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(name=name, code=code, nuip=nuip, gs=gs, hours=hours, password=hashed_password, role=role, state=state)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado con éxito'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nuip = data['nuip']
    password = data['password']

    user = User.query.filter_by(nuip=nuip).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({'message': 'Credenciales inválidas'}), 401

    if not user.state:
        return jsonify({'message': 'El usuario está deshabilitado'}), 401

    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({'access_token': access_token, 'user': user.name}), 200

@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Generar código de 6 dígitos
    code = str(random.randint(100000, 999999))

    redis_client = get_redis_client()

    redis_client.setex(f"verification_code:{email}", 600, code)

    redis_client.setex(f"email_for_code:{code}", 600, email)

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
        redis_client = get_redis_client()
        email = redis_client.get(f"email_for_code:{code}")
        if not email:
            return jsonify({"error": "Código expirado o no válido"}), 400
        reset_token = secrets.token_urlsafe(32)
        
        # Guardarlo en Redis con un TTL de 30 minutos (1800 segundos)
        redis_client.setex(f"reset_token:{reset_token}", 1800, email)
        redis_client.setex(f"reset_email:{email}", 1800, reset_token)
        return jsonify({"reset_token": reset_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

     
     
@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('reset_token')
        new_password = data.get('new_password')

        redis_client = get_redis_client()
        email = redis_client.get(f"reset_token:{token}")
        print(email)
        
        if not email:
            return jsonify({"error": "Token expirado o no válido"}), 400
        
        email_decode = email.decode("utf-8")
        user = User.query.filter_by(email=email_decode).first()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user.password = generate_password_hash(new_password)
        db.session.commit()

        redis_client.delete(f"reset_email:{token}")
        redis_client.delete(f"reset_token:{email}")

        return jsonify({"message": "Contraseña actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route('/get_password', methods=['GET'])
def get_password():
    code = request.args.get("code")
    user = User.query.filter_by(code=code).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    return jsonify({"password": user.password}), 200
from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from flask_jwt_extended import create_access_token
from flask_bcrypt import Bcrypt
from controller.qrController import generate_qr

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
    return jsonify({'access_token': access_token, 'user': user.name, 'role' : user.role}), 200
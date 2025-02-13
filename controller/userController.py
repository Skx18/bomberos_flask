from flask import jsonify, request
from models.user import User
from models.db import db

def get_all_users_controller():
    return [user.to_dict() for user in User.query.filter_by(state = True).all()], 200

def get_user_by_code_controller(code):
    try:
        user = User.query.filter_by(code=code, state = True).first()
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        return user.to_dict(), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def create_user_controller(data):
    try:
        data = request.get_json()

        new_user = User(
            name=data["name"],
            code=data.get("code", data["nuip"]),
            nuip=data["nuip"],
            gs=data["gs"],
            hours=data["hours"],
            password=data.get("code", data["nuip"]),
            role=data["role"]
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Usuario creado correctamente", "id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def update_user_controller(code, data):
    try:
        user = User.query.filter_by(code=code).first()
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        user.name = data.get("name", user.name)
        user.code = data.get("code", user.code)
        user.nuip = data.get("nuip", user.nuip)
        user.gs = data.get("gs", user.gs)
        user.hours = data.get("hours", user.hours)
        user.password = data.get("password", user.password)
        user.role = data.get("role", user.role)

        db.session.commit()
        return jsonify({"message": "usuario_actualizado", "user": user.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def delete_user_controller(code):
    try:
        user = User.query.filter_by(code=code).first()
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        user.state = False
        db.session.commit()
        return {"message": "Usuario eliminado exitosamente"}, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def get_users_dissabled_controller():
    try:
        return [user.to_dict() for user in User.query.filter_by(state = False).all()], 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def enable_user_controller(code):
    try:
        user = User.query.filter_by(code=code).first()
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        user.state = True
        db.session.commit()
        return {"message": "Usuario habilitado exitosamente"}, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

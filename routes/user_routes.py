from flask import Blueprint, request, jsonify
from models.db import db
from models.user import User
from controller.userController import *
# Crear un Blueprint para las rutas de usuarios
user_routes = Blueprint("user_routes", __name__)

# Definir las rutas

#Ruta para crear un usuario
@user_routes.route("/users/", methods=["POST"])
def create_user():
    try:
        return create_user_controller(request.get_json())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para obtener todos los usuarios
@user_routes.route("/users/", methods=["GET"])
def get_users():
    try:
        return get_all_users_controller()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para obtener un usuario por su código
@user_routes.route("/users/<string:code>/", methods=["GET"])
def get_user(code):
    try:
        return get_user_by_code_controller(code)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para actualizar un usuario
@user_routes.route("/users/<string:code>/", methods=["PUT"])
def update_user(code):
    try:
        return update_user_controller(code, request.get_json())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para eliminar un usuario
@user_routes.route("/users/<string:code>/", methods=["DELETE"])
def delete_user(code):
    try:
        return delete_user_controller(code)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para obtener los usuarios deshabilitados
@user_routes.route("/users/disabled/", methods=["GET"])
def get_users_disabled():
    try:
        return get_users_dissabled_controller()
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para habilitar un usuario
@user_routes.route("/users/enable/<string:code>/", methods=["PUT"])
def enable_user(code):
    try:
        return enable_user_controller(code)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para obtener las horas
@user_routes.route("/users/attendances/<string:date>/", methods=["GET"])
def get_hours_by_date(date):
    try:
        return get_hours_by_date_controller(date)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

#Ruta para obtener las horas por mes
@user_routes.route("/users/attendances/<int:month>/<int:year>/", methods=["GET"])
def get_hours_by_month(month, year):
    try:
        return get_hours_by_month_controller(month, year)
    except Exception as e:
        return jsonify({"error": str(e)}), 400   

#Ruta para obtener las horas por año
@user_routes.route("/users/attendances/<int:year>/", methods=["GET"])
def get_hours_by_year(year):
    try:
        return get_hours_by_year_controller(year)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

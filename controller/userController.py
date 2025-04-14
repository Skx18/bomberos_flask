from datetime import datetime
from flask import jsonify, request
from sqlalchemy import extract
from models.attendance import Attendance
from models.user import User
from models.db import db
from datetime import datetime, date
from models.attendance import Attendance
from sqlalchemy import and_, extract
from flask_bcrypt import Bcrypt
from controller.qrController import generate_qr
import requests


bcrypt = Bcrypt()

API_URL = "http://localhost:8080/fingerprint/register"

def get_all_users_controller():
    try:
        return [user.to_dict() for user in User.query.all()], 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


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
        response = requests.post(API_URL)
        
        
        if response.status_code == 200:
            fingerprint_data = response.content 
            
        else:
            return f"Error al registrar huella: {response.text}"
        
        
        if not fingerprint_data:
            return jsonify({"error": "No se pudo registrar la huella"}), 400
    
        user = User.query.filter_by(code=data["code"]).first()
        user2 = User.query.filter_by(nuip=data["nuip"]).first()
        if user:
            return jsonify({"message": "El codigo de bombero " + data["code"] + " ya está en uso"}), 400
        if user2:
            return jsonify({"message": "El número de identificación " + data["nuip"] + " ya está en uso"}), 400
        data = request.get_json()
        
        password_hash = bcrypt.generate_password_hash(data["code"]).decode('utf-8')

        new_user = User(
            name=data["name"],
            code=data.get("code", data["nuip"]),
            nuip=data["nuip"],
            gs=data["gs"],
            hours=data["hours"],
            email=data["email"],
            password=password_hash,
            role=data["role"],
            state=True,
            fingerPrint=fingerprint_data
        )


        generate_qr(new_user)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "Usuario creado correctamente", "id": new_user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def update_fingerprint(data):
    try:
        data = request.get_json()
        code = data["code"]
        user = User.query.filter_by(code = code).first()
        response = requests.post(API_URL)
        
        
        if response.status_code == 200:
            fingerprint_data = response.content  
            
        else:
            return f"Error al registrar huella: {response.text}"
        
        if not fingerprint_data:
            return jsonify({"error": "No se pudo registrar la huella"}), 400
        
        user.fingerPrint = fingerprint_data
        db.session.commit()

        return jsonify({"message": "Huella del usuario actualizada exitosamente"}), 200
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
        user.email = data.get("email", user.password)
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

def disable_user_controller(code):
    try:
        user = User.query.filter_by(code=code).first()
        if not user:
            return jsonify({"message": "Usuario no encontrado"}), 404
        user.state = False
        db.session.commit()
        return {"message": "Usuario deshabilitado exitosamente"}, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

def get_hours_by_date_controller(date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        users = User.query.all()
        print(users)
        if not users:
            return jsonify({"message": "No hay usuarios"}), 404
        info = []
        for u in users:
            print(date_obj.date())
            att = Attendance.query.filter_by(user_id=u.id, date=date_obj.date()).all()
            print("attendances", att)
            if att:
                hours = 0
                for att in att:    
                    hours += att.hours if att.hours else 0
                    user = User.query.filter_by(id=att.user_id).first()
                info.append({
                    "hours": round(hours, 2),
                    "info": user.to_dict()
                })
            else:
                info.append({
                    "hours": 0,
                    "info": u.to_dict()
                })
        return jsonify(info), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
def get_hours_by_month_controller(month, year):
    try:
        users = User.query.all()
        info = []
        if not users:
            return jsonify({"message": "No hay usuarios"}), 404
        for u in users:
            total_hours = 0
            attendances = Attendance.query.filter(
            Attendance.user_id == u.id,
            extract('month', Attendance.date) == month,
            extract('year', Attendance.date) == year).all()
            if attendances:
                hours = 0
                for att in attendances:
                    hours = 0
                    check_in_dt = datetime.combine(att.date, att.check_in)
                    check_out_dt = datetime.combine(att.date, att.check_out)
                    hours = (check_out_dt - check_in_dt).total_seconds() / 3600
                    total_hours += round(hours, 2)
                    print(att.date.month, att.date.year)
                    print(month, year)
                    hours += att.hours if att.hours else 0
                total_hours += round(hours, 2)
                print(total_hours)
                info.append({
                    "hours": total_hours,
                    "info": u.to_dict()
                })   
                db.session.commit()
            else:
                info.append({
                    "hours": 0,
                    "info": u.to_dict()
                })
        return jsonify(info), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def get_hours_by_year_controller(year):
    try:
        users = User.query.all()
        info = []
        if not users:
            return jsonify({"message": "No hay usuarios"}), 404
        for u in users:
            total_hours = 0
            attendances = Attendance.query.filter(Attendance.user_id == u.id, extract('year', Attendance.date) == year).all()
            if attendances:
                hours = 0
                for att in attendances:
                    hours += att.hours if att.hours else 0
                total_hours += round(hours, 2)
                info.append({
                    "hours": total_hours,
                    "info": u.to_dict()
                })   
                db.session.commit()
            else:
                info.append({
                    "hours": 0,
                    "info": u.to_dict()
                })
        return jsonify(info), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400



def get_user_hours_by_date_controller(day, month, year, nuip):
    try:
      
        year, month, day = int(year), int(month), int(day)
        date = datetime(year, month, day).date()

        user = User.query.filter_by(nuip=nuip).first()
        print(user)

        if not user:
            return jsonify({"error": "usuario no existe"}), 404

        attendances = Attendance.query.filter(
            and_(Attendance.user_id == user.id, Attendance.date == date)
        ).all()
        print(attendances)

        hours = sum(attendance.hours if attendance.hours else 0 for attendance in attendances)
        hours = round(hours, 2)

        return jsonify({"hours": hours}), 200

    except Exception as e:
        return jsonify({"error:": str(e)}), 500


def get_hours_by_month_year(month, year, nuip):
    
    try:
        
        user = User.query.filter_by(nuip = nuip).first()

        if not user:
            return jsonify({"error:": "Usuario no existe"}),400
        
        # If month is 0, it means we want to get the total hours for the year
        if month == 0:
            attendances = Attendance.query.filter(
                and_(Attendance.user_id == user.id, extract('year', Attendance.date) == year)
            ).all()
            
            hours = 0
            for attendance in attendances:
                hours += attendance.hours if attendance.hours else 0
            hours = round(hours, 2)
            return jsonify({"hours": hours}), 200
        else:
            query_date = date(year, month, 1)

            attendances = Attendance.query.filter(
                extract('year', Attendance.date) == query_date.year, extract('month', Attendance.date) == query_date.month
            ).all()
        
            hours = 0
            for attendance in attendances:
                hours += attendance.hours if attendance.hours else 0 
                
            hours = round(hours, 2)
            return jsonify({"hours": hours}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




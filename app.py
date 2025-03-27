import ctypes
from flask import Flask, jsonify
from models.db import db  # Asegúrate de que db ya está definido en models/db.py
from models.user import User
from models.attendance import Attendance
from flask_mail import Mail
from flask_cors import CORS
from routes.attendance_routes import attendance_routes
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from routes.auth_routes import register_routes
from routes.user_routes import user_routes 
from routes.qr_routes import register_route_qr
from routes.attendance_routes import register_routes_attendance
import os
import qrcode
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Inicializar extensiones
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()

QR_FOLDER = "qr_codes"

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = "tu_secreto"

    #Configuración correo
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'soportedeaplicacion2025@gmail.com'
    app.config['MAIL_PASSWORD'] = 'twie ogxx rmhq mdex'


    cloudinary.config(
    cloud_name= os.getenv("CLOUD_NAME"),
    api_key= os.getenv("API_KEY"),
    api_secret= os.getenv("API_SECRET")
)
    

    # Inicializar extensiones con la app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Registrar los Blueprints (rutas)
    app.register_blueprint(user_routes)
    app.register_blueprint(attendance_routes)
    # Registrar rutas de autenticación
    register_routes(app)
    register_routes_attendance(app)
    # Registrar rutas del qr
    register_route_qr(app)
    # Configurar CORS
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})

    return app

app = create_app()

with app.app_context():
    db.create_all()
    
@app.route('/')
def home():
    return "Base de datos configurada con SQLAlchemy"

if __name__ == '__main__':
    app.run(debug=True)


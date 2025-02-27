from flask import Flask
from flask_mail import Mail
from flask_redis import FlaskRedis
from models.db import db
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from routes.auth_routes import auth_bp, register_routes
from routes.user_routes import user_routes
from routes.attendance_routes import attendance_routes

# 📌 Inicializar extensiones
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app():
    app = Flask(__name__)

    # 📌 Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 📌 Configuración de autenticación
    app.config['JWT_SECRET_KEY'] = "tu_secreto"

    # 📌 Configuración de correo
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'nicelooknk2024@gmail.com'
    app.config['MAIL_PASSWORD'] = 'aynk tzti jvxl oizi'

    # 📌 Configuración de Redis
    app.config["REDIS_URL"] = "redis://localhost:6379/0"
    redis_client = FlaskRedis(app)
    print(redis_client)  # Debería mostrar un objeto válido, no `None`


    # 📌 Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    redis_client.init_app(app)

    # 📌 Registrar Blueprints (rutas)
    app.register_blueprint(user_routes)
    app.register_blueprint(attendance_routes)
    
    # Registrar rutas de autenticación
    register_routes(app)

    # 📌 Configurar CORS
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



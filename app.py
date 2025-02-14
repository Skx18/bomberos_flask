from flask import Flask
from models.db import db  # Asegúrate de que db ya está definido en models/db.py
from models.user import User
from models.attendance import Attendance
from flask_cors import CORS
from routes.attendance_routes import attendance_routes
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from routes.auth_routes import register_routes
from routes.user_routes import user_routes 

# Inicializar extensiones
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = "tu_secreto"

    # Inicializar extensiones con la app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

# Registrar los Blueprints (rutas)
app.register_blueprint(user_routes)
app.register_blueprint(attendance_routes)

    # Configurar CORS
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})

    # Registrar rutas
    register_routes(app)
    # Registrar los Blueprints (rutas)
    app.register_blueprint(user_routes)

    return app

app = create_app()

with app.app_context():
    db.create_all()
    
@app.route('/')
def home():
    return "Base de datos configurada con SQLAlchemy"

if __name__ == '__main__':
    app.run(debug=True)


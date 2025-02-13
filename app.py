from flask import Flask
from models.db import db
from models.user import User
from models.attendance import Attendance
from flask_cors import CORS
from routes.user_routes import user_routes 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

CORS(app)

CORS(app, origins=["http://localhost:5173"])

# Registrar los Blueprints (rutas)
app.register_blueprint(user_routes)

# Crear la base de datos
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Base de datos configurada con SQLAlchemy"

if __name__ == '__main__':
    app.run(debug=True)

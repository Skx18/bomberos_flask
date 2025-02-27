from flask import Blueprint, request, jsonify, send_file
from models.db import db
import qrcode
import os
from models.user import User

qr_bp = Blueprint('qr', __name__)

QR_FOLDER = "qr_codes"

def generate_qr(user):
    print(user.name, user.code)
    qr = qrcode.make(str(user.code))
    qr_path = os.path.join(QR_FOLDER, f"user_{user.code}.png")
    qr.save(qr_path)

    user.qr_code_path = qr_path
    db.session.commit()
    return qr_path


@qr_bp.route('get_qr/<int:user_id>', methods = ['GET'])
def get_qr(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return send_file(user.qr_code_path, mimetype="image/png"), 201
        else:
            return jsonify({"error:": "user no existe"}), 400
    except Exception as e:
        return jsonify({"error:": str(e)}), 500

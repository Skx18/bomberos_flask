from flask import Blueprint, request, jsonify, send_file
from models.db import db
import qrcode
from models.user import User
import cloudinary.uploader
import io 

qr_bp = Blueprint('qr', __name__)


def generate_qr(user):
    try:
        qr = qrcode.make(str(user.code))

        img_io = io.BytesIO()
        qr.save(img_io, format="PNG")
        
        img_io.seek(0)

        result = cloudinary.uploader.upload(img_io, folder="qrcodes/")

        image_url = result['secure_url']

        user.qr_code_path = image_url

        db.session.add(user)

        db.session.commit()

        return image_url
    except Exception as e:
        return str(e)


@qr_bp.route('get_qr/<int:user_id>', methods = ['GET'])
def get_qr(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify({"qr_url:": user.qr_code_path}), 201
        else:
            return jsonify({"error:": "user no existe"}), 400
    except Exception as e:
        return jsonify({"error:": str(e)}), 500

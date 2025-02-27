from controller.qrController import qr_bp

def register_route_qr(app):
    app.register_blueprint(qr_bp, url_prefix='/qr')

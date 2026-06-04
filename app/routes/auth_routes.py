from flask import Blueprint, jsonify, request
from app.models import Usuario


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/verificar-email", methods=["GET"])
def verificar_email():
    email = request.args.get("email", "").strip().lower()

    if not email:
        return jsonify({"Existe": False})

    return jsonify({"Existe": Usuario.query.filter_by(email=email).first() is not None})

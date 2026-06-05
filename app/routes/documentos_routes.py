from flask import Blueprint, render_template
from flask_login import login_required, current_user

documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos")


@documentos_bp.route("/")
@login_required
def index():
    return render_template("documentos/documentos.html", title="Meus Documentos", usuario=current_user)


@documentos_bp.route("/novo")
@login_required
def novo_documento():
    return render_template("documentos/novo_documento.html", title="Novo Documento", usuario=current_user)

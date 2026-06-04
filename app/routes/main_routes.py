from flask import Blueprint, render_template, flash

from app.forms.usuario_form import CadastroUsuarioForm
from app.services.usuario_services import criar_usuario

main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    form_registro = CadastroUsuarioForm()

    if form_registro.validate_on_submit():
        try:
            _, chave_privada_pem = criar_usuario(
                nome=form_registro.nome.data,
                email=form_registro.email.data,
                oab=form_registro.oab.data,
                senha=form_registro.senha.data,
                cargo=form_registro.cargo.data,
                senha_chave=form_registro.senha_chave.data
            )

            return render_template(
                "index.html",
                title="Cadastro Realizado",
                form_registro=CadastroUsuarioForm(),
                abrir_modal_download=True,
                chave_privada=chave_privada_pem
            )
        except ValueError as e:
            flash(str(e), "error")

    return render_template(
        "index.html",
        title="Login e Cadastro",
        form_registro=form_registro,
        abrir_modal_registro=True
    )

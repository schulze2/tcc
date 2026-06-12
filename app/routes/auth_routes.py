"""Rotas de autenticacao e verificacao de conta."""

from flask import Blueprint, jsonify, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, current_user, login_required
from app.models import Usuario
from app.forms.usuario_form import LoginForm, CadastroUsuarioForm
from app.services.usuario_services import autenticar_usuario


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/verificar-email", methods=["GET"])
def verificar_email():
    """Verifica se um e-mail ja esta cadastrado para uso no formulario."""
    email = request.args.get("email", "").strip().lower()

    if not email:
        return jsonify({"Existe": False})

    return jsonify({"Existe": Usuario.query.filter_by(email=email).first() is not None})


@auth_bp.route("/login", methods=["POST"])
def login():
    """Autentica o usuario e responde com redirect HTML ou JSON para AJAX."""
    form_login = LoginForm()
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if form_login.validate_on_submit():
        try:
            usuario = autenticar_usuario(
                email=form_login.email.data,
                senha=form_login.senha.data
            )

            login_user(usuario, remember=form_login.lembrar_me.data)

            if is_ajax:
                return jsonify({"ok": True, "success": True, "redirect_url": url_for("dashboard.index")})

            return redirect(url_for("dashboard.index"))

        except ValueError as e:
            if is_ajax:
                return jsonify({"ok": False, "message": str(e), "error": str(e)}), 401

            flash(str(e), "error")

    if is_ajax:
        mensagem = next(iter(form_login.errors or form_login.senha.errors or [
                        "Verifique os dados informados."]), "Verifique os dados informados.")

        return jsonify({"ok": False, "message": mensagem, "mensagem": mensagem}), 400

    return render_template(
        "index.html",
        title="Login e Cadastro",
        form_login=form_login,
        form_registro=CadastroUsuarioForm(),
        abrir_modal_login=True
    )


@auth_bp.route("/logout")
@login_required
def logout():
    """Encerra a sessao do usuario autenticado."""
    logout_user()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("main.index"))

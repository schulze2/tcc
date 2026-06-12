"""Rotas da area de dashboard do usuario autenticado."""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    """Renderiza a pagina principal do dashboard."""
    return render_template("dashboard.html", title="Dashboard", usuario=current_user)


@dashboard_bp.route("/pesquisa")
@login_required
def pesquisa():
    """Renderiza a tela de pesquisa de documentos do dashboard."""
    return render_template("pesquisa.html", title="Pesquisar Documentos", usuario=current_user)


@dashboard_bp.route("/configuracoes")
@login_required
def configuracoes():
    """Renderiza a tela de configuracoes do usuario no dashboard."""
    return render_template("configuracoes.html", title="Configurações", usuario=current_user)

"""Registro central dos blueprints de rotas da aplicacao."""

from app.routes.main_routes import main_bp
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.documentos_routes import documentos_bp


def register_blueprints(app):
    """Registra todos os blueprints no objeto Flask informado."""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(documentos_bp)

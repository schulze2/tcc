from app.routes.main_routes import main_bp
from app.routes.auth_routes import auth_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

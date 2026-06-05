from flask import Flask
from app.extensions import db, login_manager
from app.config import DevelopmentConfig
from app import models
from app.routes import register_blueprints


def create_app():

    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.index"

    _ = models

    @login_manager.user_loader
    def load_user(user_id):
        return models.Usuario.query.get(int(user_id))

    register_blueprints(app)

    return app

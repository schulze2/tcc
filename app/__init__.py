from flask import Flask
from app.extensions import db
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

    _ = models

    register_blueprints(app)

    return app

from flask import Flask

from config import DevelopmentConfig, ProductionConfig


def create_app(config_class=None):
    app = Flask(__name__, template_folder="templates")

    if config_class is None:
        env = ProductionConfig
        if app.config.get("DEBUG") or (env.FLASK_ENV == "development"):
            env = DevelopmentConfig
        config_class = env

    app.config.from_object(config_class)

    from app.routes.api import api
    from app.routes.web import web

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(web)

    return app

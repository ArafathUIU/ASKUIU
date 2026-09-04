import logging
import os
import sys

from flask import Flask

from config import DevelopmentConfig, ProductionConfig


def configure_logging(level=logging.INFO):
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)


def create_app(config_class=None):
    project_root = os.path.dirname(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static"),
    )

    if config_class is None:
        if os.getenv("FLASK_ENV") == "production":
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig

    app.config.from_object(config_class)

    if app.config.get("DEBUG"):
        configure_logging(level=logging.DEBUG)
    else:
        configure_logging(level=logging.INFO)

    from app.rag.service import rag_service
    rag_service.init_app(app)

    from app.routes.api import api
    from app.routes.web import web

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(web)

    return app


_app_instance = None


def __getattr__(name):
    global _app_instance
    if name == "app":
        if _app_instance is None:
            _app_instance = create_app()
        return _app_instance
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


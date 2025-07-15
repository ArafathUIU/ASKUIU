from flask import Flask
from .routes.api import api_bp
from .routes.web import web_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    return app
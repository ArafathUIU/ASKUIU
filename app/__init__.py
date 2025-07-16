# C:\xampp\htdocs\AskUIU\ASKUIU\app\__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'

    from app.routes.api import api
    from app.routes.web import web
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(web)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Opencode Go LLM configuration
    OPENCODEGO_API_KEY = os.getenv('OPENCODEGO_API_KEY')
    OPENCODEGO_BASE_URL = os.getenv('OPENCODEGO_BASE_URL', 'https://opencode.ai/zen/go/v1')
    OPENCODEGO_MODEL = os.getenv('OPENCODEGO_MODEL', 'kimi-k2.7-code')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # LLM Provider: 'auto', 'groq', 'gemini', 'opencodego', 'openai'
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'auto')

    # Groq configuration (Ultra-fast LPU inference)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'qwen/qwen3.8-27b')


    # Google Gemini configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    # Opencode Go LLM configuration
    OPENCODEGO_API_KEY = os.getenv('OPENCODEGO_API_KEY')
    OPENCODEGO_BASE_URL = os.getenv('OPENCODEGO_BASE_URL', 'https://opencode.ai/zen/go/v1')
    OPENCODEGO_MODEL = os.getenv('OPENCODEGO_MODEL', 'kimi-k2.7-code')

    # OpenAI / Compatible configuration (Ollama, DeepSeek, OpenAI)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
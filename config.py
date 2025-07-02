import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key'
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY')
    DEBUG = os.getenv('DEBUG') == 'True'
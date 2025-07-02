import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key'
    API_SECRET_KEY = os.environ.get('API_SECRET_KEY')
    #API_SECRET_KEY='47c153110cf7eb8fe2c16283b89f6927'
    DEBUG = os.getenv('DEBUG') == 'True'
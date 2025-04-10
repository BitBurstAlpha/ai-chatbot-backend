import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env file

class Config:
    
    # Debug Mode
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    APP_NAME = os.getenv('APP_NAME')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')

def get_config():
    return Config
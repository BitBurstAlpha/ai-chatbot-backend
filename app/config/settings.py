import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env file

class Config:

    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL')
    
    # Debug Mode
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    APP_NAME = os.getenv('APP_NAME')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'tmp')
    
    S3_BUCKET = os.getenv('S3_BUCKET')
    S3_REGION = os.getenv('S3_REGION')
    S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')

def get_config():
    return Config
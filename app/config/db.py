import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env file

class DatabaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
def get_db_config():
    return DatabaseConfig
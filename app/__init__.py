from flask import Flask
from flask_cors import CORS

from app.extensions import db, migrate
from .config.settings import get_config
from .config.db import get_db_config
from .api.v1 import api_v1_bp
from flask_jwt_extended import JWTManager

# import models here, as they depend on the database setup and migration status.
from app.models import *


def create_app(test_config):
    app = Flask(__name__)

     # List of allowed origins (production + local dev)
    allowed_origins = [
        "https://ai-chatbot-beta-azure.vercel.app",
        "http://localhost:3000"  # Add other environments as needed
    ]

    # Configure CORS
    CORS(
        app,
        resources={
            r"/api/v1/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
                "allow_headers": ["Content-Type", "Authorization"]  # Allowed headers
            }
        },
        supports_credentials=True  # Enable if using cookies/auth
    )

    app.config.from_object(get_config())
    app.config.from_object(get_db_config())

    if test_config is not None:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app) 
   
    # register blueprint
    app.register_blueprint(api_v1_bp , url_prefix='/api/v1')

    return app
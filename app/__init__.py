from flask import Flask

from app.extensions import db, migrate
from .config.settings import get_config
from .config.db import get_db_config
from .api.v1 import api_v1_bp
from flask_jwt_extended import JWTManager

# import models here, as they depend on the database setup and migration status.
from app.models import *


def create_app():
    app = Flask(__name__)

    app.config.from_object(get_config())
    app.config.from_object(get_db_config())

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app) 
   
    # register blueprint
    app.register_blueprint(api_v1_bp , url_prefix='/api/v1')

    return app
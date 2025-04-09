from flask import Flask

from .api.v1 import api_v1_bp

def create_app():
    app = Flask(__name__)
   
    # register blueprint
    app.register_blueprint(api_v1_bp , url_prefix='/api/v1')

    return app
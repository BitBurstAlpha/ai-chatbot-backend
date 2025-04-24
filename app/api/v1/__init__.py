from flask import Blueprint

api_v1_bp = Blueprint('api_v1', __name__)

from . import basic
from . import ticket
from . import auth
from . import user
from . import knowledge
from . import chatbot
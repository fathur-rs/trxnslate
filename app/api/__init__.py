from flask import Blueprint

model_blueprint = Blueprint('model', __name__)
auth_blueprint = Blueprint('auth', __name__)

from . import model_routes, auth_routes

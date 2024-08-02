from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .extensions.db import db
from .models.dbSchema import User, Admin
from flask_jwt_extended import JWTManager

from . import create_admin

import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
        
    # Configuration settings
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') or 'default-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    if not app.config['JWT_SECRET_KEY']:
        raise ValueError("No JWT_SECRET_KEY set for application")
    
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise ValueError("No database URI set for application")

    # Initialize Extensions
    db.init_app(app)
    jwt = JWTManager(app)
    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per hour"])

    with app.app_context():
        db.create_all()

    # Import Blueprint
    from app.api.model_routes import model_blueprint
    from app.api.auth_routes import auth_blueprint

    # Limiter
    limiter.limit("10 per minute")(model_blueprint)

    # CORS
    CORS(app, resources={
        r"/api/model/*": {"origins": os.getenv('MODEL_ALLOWED_ORIGIN', '*')},
        r"/api/auth/*": {"origins": os.getenv('AUTH_ALLOWED_ORIGIN', '*')}
    })
    
    
    # Register Blueprint
    app.register_blueprint(model_blueprint, url_prefix='/api/model')
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    
    create_admin.init_app(app)
    
    return app

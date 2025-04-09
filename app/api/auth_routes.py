from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from datetime import datetime
from app.api import auth_blueprint
from sqlalchemy.exc import IntegrityError
from ..utilities import make_response_util, admin_required
from ..models import dbSchema, authSchema
from ..extensions.db import db
from werkzeug.security import generate_password_hash, check_password_hash

@auth_blueprint.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            current_app.logger.warning("⚠️ No data provided or Invalid JSON data")
            return make_response_util(400, description="No data provided or Invalid JSON data", error="Bad Request")
        
        user_data = authSchema.Register(**data)
        username = user_data.username
        password = user_data.password
        user_type = user_data.user_type

        existing_user = dbSchema.User.query.filter_by(username=username).first()
        existing_admin = dbSchema.Admin.query.filter_by(username=username).first()
        if existing_user or existing_admin:
            current_app.logger.warning("⚠️ User already exists: %s", username)
            return make_response_util(409, description="User already exists", error="Conflict")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)

        if user_type == "user":
            new_user = dbSchema.User(username=username, password=hashed_password)
            db.session.add(new_user)
        elif user_type == "admin":
            new_admin = dbSchema.Admin(username=username, password=hashed_password)
            db.session.add(new_admin)

        db.session.commit()
        current_app.logger.info("🎉 New %s registered: %s", user_type, username)

        return make_response_util(201, message=f"{user_type.capitalize()} created successfully")

    except IntegrityError:
        db.session.rollback()
        current_app.logger.error("❌ User creation failed due to a constraint violation")
        return make_response_util(409, description="User creation failed due to a constraint violation", error="Conflict")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("❌ Error creating new user: %s", str(e))
        return make_response_util(500, description="An error occurred during registration, Check Register JSON Schema", error="Internal Server Error")

    
@auth_blueprint.route("/delete_user/", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user():
    try:
        admin_id = get_jwt_identity()
        admin = dbSchema.Admin.query.get(admin_id)
        
        if not admin:
            current_app.logger.warning("⚠️ Admin not found")
            return make_response_util(404, description="Admin not found", error="Forbidden")
        
        user_id_to_delete = request.args.get('id', type=int)
        
        if not user_id_to_delete:
            current_app.logger.warning("⚠️ No user ID provided")
            return make_response_util(400, description="No user ID provided", error="Bad Request")
        
        user_to_delete = dbSchema.User.query.get(user_id_to_delete)
        if not user_to_delete:
            current_app.logger.warning("⚠️ User does not exist: %d", user_id_to_delete)
            return make_response_util(404, description="User does not exist", error="Not Found")
        
        user_to_delete.is_active = False
        user_to_delete.deleted_at = datetime.utcnow()
        user_to_delete.deleted_by = f"Admin {admin_id}"
        
        db.session.commit()
        
        current_app.logger.info("🗑️ User %d soft deleted by Admin %d", user_id_to_delete, admin_id)
        
        return make_response_util(200, message="User deleted successfully")
    
    except IntegrityError:
        db.session.rollback()
        current_app.logger.error("❌ User deletion failed due to a constraint violation")
        return make_response_util(409, description="User deletion failed due to a constraint violation", error="Conflict")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("❌ Error deleting user [%d]: %s", user_id_to_delete, str(e))
        return make_response_util(500, description="An error occurred during deleting user", error="Internal Server Error")
    
@auth_blueprint.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    users = dbSchema.User.query.all()
    users_list = [{'id': user.id, 'username': user.username} for user in users]
    current_app.logger.info("📋 List of users retrieved")
    return make_response_util(200, message=users_list)

@auth_blueprint.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            current_app.logger.warning("⚠️ No data provided or Invalid JSON data")
            return make_response_util(400, description="No data provided or Invalid JSON data", error="Bad Request")
        
        login_data = authSchema.Login(**data)

        Model = dbSchema.User if login_data.user_type == 'user' else dbSchema.Admin
        user = Model.query.filter_by(username=login_data.username).first()

        if user and user.is_active and check_password_hash(user.password, login_data.password):
            # Generate tokens
            access_token = create_access_token(identity=user.id, additional_claims={'user_type': login_data.user_type})
            refresh_token = create_refresh_token(identity=user.id, additional_claims={'user_type': login_data.user_type})

            # Update last login timestamp
            user.last_login = datetime.now()
            db.session.commit()

            # Log successful login
            current_app.logger.info("🔓 Successful login for %s %s", login_data.user_type, login_data.username)

            return make_response_util(200, message={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_type": login_data.user_type
            })
        
        current_app.logger.warning("⚠️ Failed login attempt for %s %s", login_data.user_type, login_data.username)
        return make_response_util(401, description="Invalid credentials", error="Unauthorized")
    
    except Exception as e:
        current_app.logger.error("❌ Login error: %s", str(e))
        return make_response_util(500, description="An error occurred during login", error="Internal Server Error")

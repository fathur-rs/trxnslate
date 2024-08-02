from flask import jsonify, make_response, request, abort
from flask_jwt_extended import get_jwt_identity
from .models import dbSchema
from functools import wraps
import jwt
import datetime
import os
from PIL import Image
import cv2
import base64
import io
import numpy as np
from jwt import ExpiredSignatureError, DecodeError, InvalidTokenError
from dotenv import load_dotenv 
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def make_response_util(status_code, message=None, description=None, error=None, additional_headers=None):
    response_content = {'status_code': status_code}
    if message:
        response_content.update({'message': message})
    if description:
        response_content.update({'description': description})
    if error:
        response_content.update({'error': error})
    response = make_response(jsonify(response_content), status_code)
    if additional_headers:
        for header, value in additional_headers.items():
            response.headers[header] = value
    return response

def generate_token(user):
    payload = {
        "user": user,
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=18000),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def token_required(f):
    @wraps(f)
    def decorated_token_required(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return make_response_util(401, description="Token is missing", error='Unauthorized')

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            return make_response_util(401, description="Token has expired", error='Unauthorized')
        except (DecodeError, InvalidTokenError):
            return make_response_util(401, description="Token is invalid", error='Unauthorized')

        return f(*args, **kwargs)
    return decorated_token_required

def admin_required(f):
    @wraps(f)
    def decorated_admin_required(*args, **kwargs):
        current_user_id = get_jwt_identity()
        admin = dbSchema.Admin.query.get(current_user_id)
        if not admin or not admin.is_active:
            abort(403, description="Admin access required")
        return f(*args, **kwargs)
    return decorated_admin_required

def base64_to_pil(base64_str):
    """Convert base64 string to PIL Image"""
    img_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_data))

def pil_to_cv2(pil_image):
    """Convert PIL Image to OpenCV format"""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
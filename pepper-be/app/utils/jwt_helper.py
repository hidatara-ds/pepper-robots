import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "robo-pepper-default-secret")

def generate_access_token(admin):
    """Generate JWT access token for authenticated admin"""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        'admin_id': admin['admin_id'],
        'email': admin['email'],
        'iat': now,
        'exp': now + datetime.timedelta(hours=24)  # Token expires in 1 day
    }
    
    access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return access_token

def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'token_expired'}
    except jwt.InvalidTokenError:
        return {'error': 'invalid_token'}

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
        except IndexError:
            return jsonify({'message': 'Invalid token format'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'message': 'Invalid token'}), 401
        
        if isinstance(payload, dict) and 'error' in payload:
            if payload['error'] == 'token_expired':
                return jsonify({'message': 'Token has expired', 'error': 'token_expired'}), 401
            else:
                return jsonify({'message': 'Invalid token', 'error': 'invalid_token'}), 401
        
        # Add current user info to request
        g.current_user = payload 
        return f(*args, **kwargs)
    
    return decorated_function
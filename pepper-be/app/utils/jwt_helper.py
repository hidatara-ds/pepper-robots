"""
JWT Helper Utilities
Functions for generating, decoding, and validating JWT tokens for authentication
"""

import jwt
import datetime
import logging
from functools import wraps
from typing import Dict, Any, Optional
from flask import request, jsonify, g
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get secret key from environment, with secure default warning
SECRET_KEY = os.getenv("SECRET_KEY", "robo-pepper-default-secret")
if SECRET_KEY == "robo-pepper-default-secret":
    logger.warning("Using default SECRET_KEY. Please set SECRET_KEY environment variable for production!")

def generate_access_token(admin: Dict[str, Any]) -> str:
    """
    Generate JWT access token for authenticated admin
    
    Args:
        admin: Dictionary containing admin information with 'admin_id' and 'email'
        
    Returns:
        Encoded JWT token string
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        'admin_id': admin['admin_id'],
        'email': admin['email'],
        'iat': now,
        'exp': now + datetime.timedelta(hours=24)  # Token expires in 24 hours
    }
    
    try:
        access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        logger.info(f"Access token generated for admin: {admin.get('email')}")
        return access_token
    except Exception as e:
        logger.error(f"Error generating access token: {e}")
        raise

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded payload dictionary if valid, or error dictionary if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        logger.debug("Token decoded successfully")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return {'error': 'token_expired'}
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return {'error': 'invalid_token'}
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        return {'error': 'token_decode_error'}

def token_required(f):
    """
    Decorator to require valid JWT token for protected routes
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route():
            user = g.current_user
            return jsonify({'message': 'Access granted'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("Authentication attempt without token")
            return jsonify({'message': 'Token is missing', 'error': 'no_token'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
        except (IndexError, AttributeError) as e:
            logger.warning(f"Invalid token format in Authorization header: {e}")
            return jsonify({'message': 'Invalid token format', 'error': 'invalid_format'}), 401
        
        payload = decode_token(token)
        if not payload:
            logger.warning("Token decode returned None")
            return jsonify({'message': 'Invalid token', 'error': 'invalid_token'}), 401
        
        if isinstance(payload, dict) and 'error' in payload:
            error_type = payload['error']
            logger.warning(f"Token validation failed: {error_type}")
            if error_type == 'token_expired':
                return jsonify({
                    'message': 'Token has expired', 
                    'error': 'token_expired'
                }), 401
            else:
                return jsonify({
                    'message': 'Invalid token', 
                    'error': error_type
                }), 401
        
        # Add current user info to Flask's g object for use in route handler
        g.current_user = payload
        logger.debug(f"Token validated for user: {payload.get('email')}")
        return f(*args, **kwargs)
    
    return decorated_function
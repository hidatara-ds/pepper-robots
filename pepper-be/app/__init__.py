"""
Pepper Robot Management Backend Application
Main Flask application initialization with rate limiting and API documentation
"""

import os
import logging
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load Flask configuration from environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://",
)

# Initialize Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Pepper Robot Management API",
        "description": "API for managing Pepper Robot user identities and face recognition",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@pepper-robot.com"
        }
    },
    "host": "127.0.0.1:5000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token authentication. Format: Bearer <token>"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Import routes after app initialization to avoid circular imports
from app import routes

logger.info("Pepper Robot Management API initialized successfully")

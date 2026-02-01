"""
Application Entry Point
Main script to run the Pepper Robot Management Backend server
"""

import os
import logging
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv('HOST', '0.0.0.0')  # Accept connections from any IP
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    flask_env = os.getenv('FLASK_ENV', 'development')
    
    logger.info("=" * 60)
    logger.info("Pepper Robot Management Backend Server")
    logger.info("=" * 60)
    logger.info(f"Starting Flask server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Environment: {flask_env}")
    logger.info(f"API Documentation: http://{host}:{port}/api/docs")
    logger.info("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)

# rag/com/app.py
import os
import logging

from flask import Flask
from flask_cors import CORS
from rag.com.config import SERVER_CONFIG, LOG_LEVEL

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
if SERVER_CONFIG['cors_origins'] != ['*']:
    CORS(app, resources={
        r"/*": {
            "origins": SERVER_CONFIG['cors_origins'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
else:
    CORS(app)

# Import routes after app initialization
from rag.com import routes_ref

def start_server():
    """Start the Flask server with configured settings"""
    host = SERVER_CONFIG['host']
    port = SERVER_CONFIG['port']
    debug = SERVER_CONFIG['debug']
    
    # Log server configuration
    logger.info(f"Starting Flask server with configuration:")
    logger.info(f"Host: {host} (0.0.0.0 = all interfaces)")
    logger.info(f"Port: {port}")
    logger.info(f"Debug Mode: {debug}")
    if host == '0.0.0.0':
        logger.info(f"Server will be accessible at:")
        logger.info(f"- Local: http://127.0.0.1:{port}")
        logger.info(f"- Network: http://<your-ip>:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=SERVER_CONFIG['threaded']
    )

if __name__ == '__main__':
    start_server()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return {"error": "Not Found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal Server Error"}, 500

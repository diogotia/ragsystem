# rag/com/app.py
import os

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import routes after app is created to avoid circular imports
from rag.com import routes_ref

# Register blueprints if you have any
# app.register_blueprint(some_blueprint)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return {"error": "Not Found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal Server Error"}, 500

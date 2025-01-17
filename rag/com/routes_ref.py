import logging
import pdb
from typing import Dict, Optional
from bson import ObjectId

from flask import request, jsonify, Response
import gridfs
from werkzeug.utils import secure_filename

from rag.com.utils_ref import search, generate_answer, read_document
from rag.com.config import db, collection
from rag.com.app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'json'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/v1/endpoints', methods=['GET'])
def list_endpoints_v1():
    """List all available API endpoints."""
    endpoints = []
    for rule in app.url_map.iter_rules():
        endpoints.append({
            "url": str(rule),
            "methods": list(rule.methods)
        })
    return jsonify({"endpoints": endpoints})

@app.route('/api/v1/search', methods=['POST'])
def search_endpoint_v1():
    """Search endpoint"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400
    
    results = search(
        query=data['query'],
        include_sentiment=data.get('include_sentiment', False)
    )
    return jsonify({"results": results})

@app.route('/api/v1/generate', methods=['POST'])
def generate_endpoint_v1():
    """Generate endpoint"""
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400
    
    response = generate_answer(data['query'])
    return jsonify({"response": response})

@app.route('/api/v1/documents', methods=['GET'])
def list_documents_v1():
    """List all documents"""
    fs = gridfs.GridFS(db)
    files = []
    for grid_out in fs.find():
        files.append({
            'file_id': str(grid_out._id),
            'filename': grid_out.filename,
            'upload_date': grid_out.upload_date.strftime('%c')
        })
    return jsonify({"files": files})

@app.route('/api/v1/documents', methods=['POST'])
def upload_document_v1():
    """Upload document endpoint"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    fs = gridfs.GridFS(db)
    file_id = fs.put(file.read(), filename=file.filename)
    return jsonify({
        "message": "File uploaded successfully",
        "file_id": str(file_id)
    }), 201

@app.route('/api/v1/documents/<file_id>', methods=['GET'])
def get_document_v1(file_id):
    """Get document by ID"""
    try:
        if not ObjectId.is_valid(file_id):
            return jsonify({"error": "Invalid file ID format"}), 400
        
        fs = gridfs.GridFS(db)
        file_obj = fs.get(ObjectId(file_id))
        return jsonify({
            "content": file_obj.read().decode('utf-8'),
            "filename": file_obj.filename
        })
    except Exception as e:
        return jsonify({"error": "Document not found"}), 404 
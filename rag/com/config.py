# rag/com/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Base paths that work on both Windows and Linux
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
MODELS_DIR = BASE_DIR / 'models'

try:
    # Create necessary directories
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

# Default Model Settings
DEFAULT_MODEL_SETTINGS = {
    'MODEL_NAME_LOCAL': 'gpt2',
    'MODEL_NAME_REMOTE': 'gpt2',
    'USE_LOCAL_MODEL': True,  # Default to using local model
    'MODEL_CACHE_DIR': str(MODELS_DIR / 'gpt2')
}

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'queryDB')

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db['queries']

# Model Configuration (with defaults)
MODEL_DIR = MODELS_DIR / DEFAULT_MODEL_SETTINGS['MODEL_NAME_LOCAL']
MODEL_NAME_LOCAL = os.getenv('MODEL_NAME_LOCAL', DEFAULT_MODEL_SETTINGS['MODEL_NAME_LOCAL'])
MODEL_NAME_REMOTE = os.getenv('MODEL_NAME_REMOTE', DEFAULT_MODEL_SETTINGS['MODEL_NAME_REMOTE'])
USE_LOCAL_MODEL = os.getenv('USE_LOCAL_MODEL', str(DEFAULT_MODEL_SETTINGS['USE_LOCAL_MODEL'])).lower() == 'true'

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')  # 0.0.0.0 for all interfaces, 127.0.0.1 for localhost only
API_PORT = int(os.getenv('API_PORT', '5000'))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() == 'true'  # Default to True for development

# Network Configuration
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')  # Comma-separated list of allowed hosts
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')    # Comma-separated list of allowed CORS origins

# Server Configuration
SERVER_CONFIG = {
    'host': API_HOST,
    'port': API_PORT,
    'debug': DEBUG_MODE,
    'threaded': True,
    'allowed_hosts': ALLOWED_HOSTS,
    'cors_origins': CORS_ORIGINS
}

# Model Configuration
config = {
    'model_name_local': str(MODEL_DIR),
    'model_name_remote': MODEL_NAME_REMOTE,
    'use_local_model': USE_LOCAL_MODEL,
    'model_cache_dir': DEFAULT_MODEL_SETTINGS['MODEL_CACHE_DIR'],
    'mongo_uri': MONGO_URI,
    'db_name': DB_NAME,
    'collection_name': 'queries'
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Export all necessary variables
__all__ = [
    'API_HOST', 'API_PORT', 'DEBUG_MODE', 'SERVER_CONFIG',
    'MONGO_URI', 'DB_NAME', 'collection', 'db',
    'config', 'LOG_LEVEL', 'ALLOWED_HOSTS', 'CORS_ORIGINS'
]
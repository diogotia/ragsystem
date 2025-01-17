# rag/com/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Base paths that work on both Windows and Linux
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

try:
    # Create necessary directories
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create directories: {e}")

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'queryDB')

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db['queries']

# Model Configuration
config = {
    'model_name_or_path': os.getenv('MODEL_NAME', 'gpt2'),
    'mongo_uri': MONGO_URI,
    'db_name': DB_NAME,
    'collection_name': 'queries'
}

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '5000'))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
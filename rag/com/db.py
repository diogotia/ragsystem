from pymongo import MongoClient
from pymongo.errors import ConnectionError
import time
import logging
from rag.com.config import MONGO_URI, DB_NAME

def get_db_connection(max_retries=3, retry_delay=5):
    """Get MongoDB connection with retry logic"""
    for attempt in range(max_retries):
        try:
            client = MongoClient(MONGO_URI)
            client.server_info()  # Test connection
            return client[DB_NAME]
        except ConnectionError as e:
            if attempt == max_retries - 1:
                raise
            logging.warning(f"MongoDB connection attempt {attempt + 1} failed. Retrying...")
            time.sleep(retry_delay) 
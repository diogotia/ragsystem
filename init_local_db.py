from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['queryDB']
        
        # Create collections if they don't exist
        if 'queries' not in db.list_collection_names():
            db.create_collection('queries')
            logger.info("Created 'queries' collection")
        
        if 'documents' not in db.list_collection_names():
            db.create_collection('documents')
            logger.info("Created 'documents' collection")
        
        # Create text index on queries collection
        db.queries.create_index([('content', 'text')], name='content_text_index')
        logger.info("Created text index on 'queries' collection")
        
        # Create any additional indexes needed
        db.documents.create_index([('filename', 1)], name='filename_index')
        logger.info("Created filename index on 'documents' collection")
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == '__main__':
    init_database() 
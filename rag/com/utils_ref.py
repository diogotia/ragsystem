import os
import logging
import warnings
from typing import Dict, List, Optional, Union
from functools import lru_cache

import gridfs
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_core.prompts import PromptTemplate
from rag.com.config import config, collection, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment setup
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings('ignore', category=UserWarning)

class ModelManager:
    """Singleton class to manage model instances."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
    
    def _initialize_models(self):
        """Initialize the models lazily."""
        self.model_name_or_path = config['model_name_or_path']
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name_or_path)
        
        # Initialize sentiment analyzer
        self.sentiment_model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        self.sentiment_analyzer = pipeline("sentiment-analysis", model=self.sentiment_model_name)

# Initialize prompts
PROMPTS = {
    'qa': PromptTemplate(
        input_variables=["query"],
        template="You are an expert on quality automation. Provide a detailed and insightful answer to the following question: {query}"
    ),
    'rag': PromptTemplate(
        input_variables=["query"],
        template="You are reading document provide part of document contains: {query}"
    )
}

class DocumentSearcher:
    """Class to handle document searching and RAG operations."""
    
    def __init__(self):
        self.fs = gridfs.GridFS(db)
        self.model_manager = ModelManager()
    
    @lru_cache(maxsize=128)
    def generate_response(self, query: str) -> str:
        """Generate a response using the language model."""
        try:
            prompt_text = PROMPTS['qa'].format(query=query)
            inputs = self.model_manager.tokenizer(prompt_text, return_tensors="pt")
            outputs = self.model_manager.model.generate(
                **inputs,
                max_length=150,
                num_return_sequences=1,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            return self.model_manager.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def handle_query(self, query: str) -> str:
        """Handle a query and store the response."""
        try:
            response = self.generate_response(query)
            document = {"query": query, "response": response}
            collection.insert_one(document)
            return response
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            raise

    def search_documents(
        self,
        query: str,
        filename: Optional[str] = None,
        include_sentiment: bool = False,
        context_length: int = 100
    ) -> Dict[str, List[Dict]]:
        """
        Unified search function that handles both collection and GridFS searches.
        
        Args:
            query: Search query string
            filename: Optional specific filename to search
            include_sentiment: Whether to include sentiment analysis
            context_length: Length of the context window around found query
            
        Returns:
            Dictionary containing query results and document results
        """
        try:
            logger.info(f"Searching for query: {query}" + (f" in file: {filename}" if filename else ""))
            
            results = {
                "query_results": [],
                "document_results": []
            }
            
            # Search in collection
            if not filename:
                search_results = collection.find({"$text": {"$search": query}})
                results["query_results"] = [
                    {"query": doc["query"], "response": doc["response"]}
                    for doc in search_results
                ]
            
            # Search in GridFS documents
            grid_query = {"filename": filename} if filename else {}
            for grid_out in self.fs.find(grid_query):
                content = grid_out.read().decode('utf-8')
                start_index = content.lower().find(query.lower())
                
                if start_index != -1:
                    end_index = start_index + len(query) + context_length
                    snippet = content[start_index:end_index]
                    
                    doc_result = {
                        "filename": grid_out.filename,
                        "snippet": snippet
                    }
                    
                    # Add sentiment analysis if requested
                    if include_sentiment:
                        sentiment = self.model_manager.sentiment_analyzer(snippet)
                        doc_result["sentiment"] = {
                            "label": sentiment[0]["label"],
                            "score": sentiment[0]["score"]
                        }
                    
                    results["document_results"].append(doc_result)
            
            logger.info(f"Found {len(results['document_results'])} document results")
            return results
            
        except Exception as e:
            logger.error(f"Error in document search: {e}")
            raise

    def read_file(self, file_id: str) -> Optional[str]:
        """Read a specific file from GridFS."""
        try:
            grid_out = self.fs.get(file_id)
            return grid_out.read().decode('utf-8') if grid_out else None
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {e}")
            return None

# Create a singleton instance
document_searcher = DocumentSearcher()

# Export the main functions with simpler interfaces
def search(query: str, **kwargs) -> Dict:
    """Main search interface."""
    return document_searcher.search_documents(query, **kwargs)

def generate_answer(query: str) -> str:
    """Main generation interface."""
    return document_searcher.handle_query(query)

def read_document(file_id: str) -> Optional[str]:
    """Main document reading interface."""
    return document_searcher.read_file(file_id) 
import os
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_model(model_name='gpt2', model_dir='models/gpt2'):
    """
    Download and save the model and tokenizer.
    
    Args:
        model_name (str): Name of the model to download from HuggingFace
        model_dir (str): Directory to save the model
    """
    try:
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Check if model already exists
        if (model_path / "pytorch_model.bin").exists():
            logger.info(f"Model already exists in {model_dir}")
            return True
            
        logger.info(f"Downloading {model_name} model...")
        
        # Download and save model
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        logger.info(f"Saving model to {model_dir}")
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        
        logger.info("Model download completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading model: {str(e)}")
        return False

if __name__ == "__main__":
    # Get model directory from environment variable or use default
    model_dir = os.getenv('MODEL_PATH', 'models/gpt2')
    model_name = os.getenv('MODEL_NAME', 'gpt2')
    
    success = download_model(model_name, model_dir)
    if not success:
        exit(1) 
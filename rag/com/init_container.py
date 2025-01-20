import os
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

def init_container():
    """Initialize container with required models and setup"""
    model_dir = Path("/app/models/gpt2")
    
    # Download model if not exists
    if not (model_dir / "pytorch_model.bin").exists():
        print("Downloading GPT-2 model...")
        model = AutoModelForCausalLM.from_pretrained('gpt2')
        tokenizer = AutoTokenizer.from_pretrained('gpt2')
        
        model_dir.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        print("Model downloaded successfully!")
    else:
        print("Model already exists, skipping download") 
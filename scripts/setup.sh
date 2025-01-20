#!/bin/bash
set -e

# Create necessary directories
mkdir -p models/gpt2 data logs

# Activate virtual environment if it exists
if [ -d ".venv7" ]; then
    source .venv7/bin/activate
fi

# Install dependencies
pip install -r requirements.txt

# Download and setup model
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path

model_dir = Path('models/gpt2')
if not (model_dir / 'pytorch_model.bin').exists():
    print('Downloading GPT-2 model...')
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    print('Model downloaded successfully!')
else:
    print('Model already exists, skipping download')
"

echo "Setup completed successfully!" 
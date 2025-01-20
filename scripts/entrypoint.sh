#!/bin/bash
set -e

# Initialize container (download model if needed)
python -c "from rag.com.init_container import init_container; init_container()"

# Start the application
exec gunicorn --bind 0.0.0.0:5000 run:app 
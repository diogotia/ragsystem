#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [local|docker]"
    echo "  local  - Run tests against local server (port 5000)"
    echo "  docker - Run tests against Docker container (port 5002)"
    exit 1
}

# Check if environment argument is provided
if [ $# -ne 1 ]; then
    usage
fi

# Set environment variables based on argument
case "$1" in
    "local")
        export API_HOST=localhost
        export API_PORT=5000
        echo "Initializing local MongoDB..."
        python3 init_local_db.py
        echo "Running tests against local server..."
        pytest tests/test_api_integration.py -v
        ;;
    "docker")
        export API_HOST=localhost
        export API_PORT=5002
        echo "Running tests against Docker container..."
        pytest tests/test_api_integration.py -v
        ;;
    *)
        usage
        ;;
esac 
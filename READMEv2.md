# RAG System v2

A production-ready Question Answering system implementing RAG (Retrieval-Augmented Generation) architecture using Flask, MongoDB, and GPT-2.

## Features

- 🔍 Semantic search across documents
- 🤖 GPT-2 powered response generation
- 📚 Document management system
- 🗄️ MongoDB integration for efficient storage
- 🐳 Docker support for easy deployment
- 🔄 RESTful API endpoints
- 📊 Performance monitoring
- 🔒 Environment-based configuration

## Prerequisites

- Python 3.12+
- MongoDB 6.0+
- Docker 24.0+ and Docker Compose V2 (for containerized deployment)
- Git
- 4GB+ RAM recommended
- 2GB+ free disk space for models

## Quick Start

### Windows Quick Start

```powershell
# Clone repository
git clone <repository-url>
cd ragsystem

# Setup environment
python -m venv .venv7
.venv7\Scripts\activate
pip install -r requirements.txt

# Download model
python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; model = AutoModelForCausalLM.from_pretrained('gpt2'); tokenizer = AutoTokenizer.from_pretrained('gpt2'); model.save_pretrained('models/gpt2'); tokenizer.save_pretrained('models/gpt2')"

# Start application
python run.py
```

### Linux/MacOS Quick Start

```bash
# Clone repository
git clone <repository-url>
cd ragsystem

# Setup environment
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start application
python run.py
```

### Docker Quick Start

```bash
docker-compose up --build
```

## Detailed Setup Instructions

### Local Development Setup

#### 1. Environment Setup

Windows:
```powershell
python -m venv .venv7
.venv7\Scripts\activate
```

Linux/MacOS:
```bash
python3 -m venv .venv7
source .venv7/bin/activate
```

#### 2. Dependencies Installation

```bash
pip install -r requirements.txt
```

#### 3. MongoDB Setup

1. Install MongoDB Community Edition
2. Start MongoDB service:
   ```bash
   # Windows (in Admin PowerShell)
   net start MongoDB

   # Linux
   sudo systemctl start mongod
   ```

#### 4. Model Setup

```bash
# The script will create necessary directories and download the model
python scripts/download_model.py

# Optional: You can specify a different model or path using environment variables
MODEL_NAME=gpt2 MODEL_PATH=models/gpt2 python scripts/download_model.py
```

### Docker Deployment

#### 1. Production Deployment

```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Scale services if needed
docker-compose up -d --scale app=3

# Check container details
docker inspect my-python-app-container

# Stop and remove containers
sudo docker stop mongodb my-python-app-container && sudo docker rm mongodb my-python-app-container

# Start and run containers with volumes in one command 
sudo docker run -d --name my-python-app-container --network host -e MONGO_URI=mongodb://127.0.0.1:27017/ -e DB_NAME=queryDB -e API_PORT=5002 -e DEBUG_MODE=true -v $(pwd)/models:/app/models -v $(pwd)/logs:/app/logs my-python-app****
```

#### 2. Development Deployment

```bash
# Build and start with development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## API Usage Examples

### 1. Document Upload

```python
import requests

files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:5000/api/v1/documents', files=files)
print(response.json())
```

### 2. Query Generation

```python
import requests

query = {
    "question": "What are the key benefits of RAG architecture?",
    "max_length": 150,
    "temperature": 0.7
}
response = requests.post('http://localhost:5000/api/v1/generate', json=query)
print(response.json())

# Script for auto setup and run
python3 init_local_db.py
```

### 3. Document Search

```python
import requests

search = {
    "query": "machine learning applications",
    "limit": 5,
    "include_metadata": True
}
response = requests.post('http://localhost:5000/api/v1/search', json=search)
print(response.json())
```

## Project Structure

```
ragsystem/
├── data/               # Data storage
│   ├── documents/     # Uploaded documents
│   └── embeddings/    # Cached embeddings
├── logs/              # Application logs
├── models/            # Model storage
│   └── gpt2/         # GPT-2 model files
├── rag/               # Application code
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── models/       # Data models
│   └── utils/        # Utility functions
├── scripts/          # Utility scripts
├── tests/            # Test files
├── Dockerfile        # Main Dockerfile
├── docker-compose.yml # Docker Compose config
└── requirements.txt  # Python dependencies
```

## Configuration

### Default Settings

The system comes with pre-configured defaults for easy setup:

```python
# Default Model Settings
DEFAULT_MODEL_SETTINGS = {
    'MODEL_NAME_LOCAL': 'gpt2',
    'MODEL_NAME_REMOTE': 'gpt2',
    'USE_LOCAL_MODEL': True,  # Default to using local model
    'MODEL_CACHE_DIR': 'models/gpt2'
}
```

### Environment Variables

All settings can be overridden using environment variables:

1. **Model Configuration**
   ```env
   # Model Settings
   MODEL_NAME_LOCAL=gpt2          # Name of the local model
   MODEL_NAME_REMOTE=gpt2         # Name of the remote model from HuggingFace
   USE_LOCAL_MODEL=true          # Use local model (true) or download from HuggingFace (false)
   ```

2. **Server Configuration**
   ```env
   # API Settings
   API_HOST=0.0.0.0              # 0.0.0.0 for all interfaces, 127.0.0.1 for localhost only
   API_PORT=5000                 # Port number
   DEBUG_MODE=false             # Enable/disable debug mode
   
   # Network Settings
   ALLOWED_HOSTS=*               # Comma-separated list of allowed hosts
   CORS_ORIGINS=*               # Comma-separated list of allowed CORS origins
   ```

3. **Database Configuration**
   ```env
   # MongoDB Settings
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=queryDB
   ```

4. **Logging Configuration**
   ```env
   LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, or CRITICAL
   ```

### Configuration Precedence

The system follows this configuration precedence (highest to lowest):
1. Environment variables
2. `.env` file settings
3. Default settings in `config.py`

### Usage Examples

1. **Local Development (Default)**
   ```bash
   # Uses local model, localhost only
   export API_HOST=127.0.0.1
   export DEBUG_MODE=true
   python run.py
   ```

2. **Production Setup**
   ```bash
   # Uses local model, accessible from network
   export API_HOST=0.0.0.0
   export DEBUG_MODE=false
   export CORS_ORIGINS=https://your-frontend-domain.com
   python run.py
   ```

3. **Remote Model Usage**
   ```bash
   # Uses HuggingFace model instead of local
   export USE_LOCAL_MODEL=false
   export MODEL_NAME_REMOTE=gpt2
   python run.py
   ```

4. **Custom Model Path**
   ```bash
   # Uses a different local model
   export USE_LOCAL_MODEL=true
   export MODEL_NAME_LOCAL=custom-model
   python run.py
   ```

### Server Access

The server can be accessed in different ways depending on the configuration:

- `http://127.0.0.1:5000` - Local access only (recommended for development)
- `http://0.0.0.0:5000` - All interfaces (not for direct access)
- `http://<your-ip>:5000` - Network access (when API_HOST=0.0.0.0)

### Security Notes

1. Development:
   - Use `API_HOST=127.0.0.1` for local-only access
   - Enable `DEBUG_MODE` for detailed error messages
   - Use `CORS_ORIGINS=*` for unrestricted access

2. Production:
   - Use `API_HOST=0.0.0.0` only behind a reverse proxy
   - Disable `DEBUG_MODE`
   - Set specific `CORS_ORIGINS` and `ALLOWED_HOSTS`
   - Use HTTPS in production

## Monitoring and Maintenance

### Health Check

```bash
curl http://localhost:5000/health
```

### Performance Monitoring

```bash
# Check API response times
curl http://localhost:5000/metrics

# Monitor Docker containers
docker stats
```

### Backup MongoDB Data

```bash
# Backup
mongodump --out ./backup

# Restore
mongorestore ./backup
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py
 sample : pytest -v tests/test_api_integration.py -s

# Run with coverage
pytest --cov=rag tests/

# Run with script for local model
  ./run_tests.sh local 
# or
  ./run_tests.sh docker  

```

## Troubleshooting

Common issues and solutions:

1. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB status
   mongosh --eval "db.serverStatus()"
   ```

2. **Model Loading Issues**
   ```bash
   # Verify model files
   ls -l models/gpt2/
   ```

3. **Docker Issues**
   ```bash
   # Check container logs
   docker-compose logs app
   ```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- HuggingFace Transformers team for the GPT-2 implementation
- MongoDB team for the excellent database
- Flask team for the web framework

## Contact

Project Link: [https://github.com/diogotia/ragsystem](https://github.com/diogotia/ragsystem)

## Production Setup

### Prerequisites
- Python 3.12+
- MongoDB 4.4+
- Virtual environment (recommended)

### Production Installation
1. Install production dependencies:
```bash
pip install -r requirements.prod.txt
```

2. Configure Production Environment:
```bash
# Copy the example environment file
cp .env .env.prod

# Edit production settings
# Important settings to configure:
# - API_HOST=0.0.0.0
# - DEBUG_MODE=false
# - CORS_ORIGINS=your-domains
# - ALLOWED_HOSTS=your-domains
# - MONGO_URI=your-mongodb-uri
```

### Running in Production

1. Using Gunicorn (Linux):
```bash
# Start with default production config
gunicorn -c gunicorn.conf.py rag.com.app:app

# Or with custom workers and timeout
gunicorn -c gunicorn.conf.py \
    --workers=4 \
    --timeout=120 \
    --log-level=warning \
    rag.com.app:app
```

2. Using Waitress (Windows):
```bash
waitress-serve --port=5000 --call rag.com.app:app
```

### Production Configuration

#### Environment Variables
```ini
# Server Settings
API_HOST=0.0.0.0          # Listen on all interfaces
API_PORT=5000             # Port number
DEBUG_MODE=false          # Disable debug mode
LOG_LEVEL=WARNING         # Production log level

# Security Settings
CORS_ORIGINS=https://your-domain.com,https://api.your-domain.com
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# Database Settings
MONGO_URI=mongodb://your-mongodb-host:27017/
DB_NAME=queryDB

# Performance Settings
WORKERS=4                 # Gunicorn workers
TIMEOUT=120              # Request timeout
MAX_REQUESTS=1000        # Requests per worker
```

#### Gunicorn Configuration
The `gunicorn.conf.py` file contains production-ready settings:
- Auto-scaled workers based on CPU cores
- Request limits for security
- Logging configuration
- Process management
- Keep-alive settings

### Production Best Practices

1. Security:
   - Always use HTTPS in production
   - Set specific CORS_ORIGINS and ALLOWED_HOSTS
   - Keep DEBUG_MODE=false
   - Use secure MongoDB credentials

2. Performance:
   - Adjust workers based on server capacity
   - Monitor memory usage
   - Set appropriate timeouts
   - Use connection pooling for MongoDB

3. Monitoring:
   - Configure access and error logs
   - Set up monitoring (Prometheus metrics available)
   - Use Sentry for error tracking

4. Deployment:
   - Use process manager (systemd, supervisor)
   - Set up health checks
   - Configure automatic restarts
   - Use rolling updates

### Maintenance

1. Log Rotation:
```bash
# Example logrotate configuration
/path/to/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        kill -USR1 $(cat /path/to/gunicorn.pid)
    endscript
}
```

2. Backup:
   - Regular MongoDB backups
   - Environment configuration backup
   - Model files backup

3. Updates:
   - Regular security updates
   - Dependency updates
   - Model updates

4. Monitoring:
   - CPU/Memory usage
   - Request latency
   - Error rates
   - Database performance

### Systemd Service Installation (Linux)

1. Copy the service file:
```bash
sudo cp rag-api.service /etc/systemd/system/
```

2. Create application directory:
```bash
sudo mkdir -p /opt/rag-api
sudo chown www-data:www-data /opt/rag-api
```

3. Deploy application:
```bash
# Copy application files
sudo cp -r . /opt/rag-api/

# Create virtual environment
cd /opt/rag-api
sudo -u www-data python3 -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.prod.txt

# Copy and edit production environment file
sudo cp .env .env.prod
sudo nano .env.prod
```

4. Start and enable the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start rag-api

# Enable on boot
sudo systemctl enable rag-api

# Check status
sudo systemctl status rag-api
```

5. View logs:
```bash
# View service logs
sudo journalctl -u rag-api -f

# View application logs
sudo tail -f /opt/rag-api/logs/error.log
sudo tail -f /opt/rag-api/logs/access.log
``` 
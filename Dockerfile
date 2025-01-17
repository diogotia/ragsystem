FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements/prod.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/data /app/logs \
    && chmod -R 755 /app/data /app/logs

# Environment variables
ENV MONGO_URI=mongodb://mongodb:27017/
ENV DB_NAME=queryDB
ENV API_PORT=5000
ENV API_HOST=0.0.0.0
ENV DEBUG_MODE=False
ENV LOG_LEVEL=INFO

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"] 
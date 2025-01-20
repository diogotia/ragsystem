FROM mongo:5.0

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set up Python environment
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy MongoDB initialization script
COPY init-mongo.js /docker-entrypoint-initdb.d/

# Create directories for models and logs
RUN mkdir -p /app/models /app/logs

# Set environment variables
ENV MONGO_URI=mongodb://localhost:27017/
ENV DB_NAME=queryDB
ENV DEBUG_MODE=true
ENV LOG_LEVEL=INFO

# Update entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000 27017

ENTRYPOINT ["/app/entrypoint.sh"] 
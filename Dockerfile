# Use a specific MongoDB version for reproducibility
FROM mongo:5.0.31

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
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY . .

# Copy MongoDB initialization script
COPY init-mongo.js /docker-entrypoint-initdb.d/

# Create directories for models and logs
RUN mkdir -p /app/models /app/logs \
    && mkdir -p /var/log/mongodb \
    && chown -R mongodb:mongodb /var/log/mongodb

# Set environment variables
ARG MONGO_URI=mongodb://localhost:27017/
ENV MONGO_URI=$MONGO_URI
ENV DB_NAME=queryDB
ENV DEBUG_MODE=true
ENV LOG_LEVEL=INFO

# Copy entrypoint script
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 5000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
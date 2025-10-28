#!/bin/bash

# Start MongoDB in the foreground (for debugging purposes)
echo "Starting MongoDB..."
mongod --port 27017 --bind_ip_all &

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to be ready..."
until mongosh --port 27017 --eval "print('MongoDB is ready')" > /dev/null 2>&1; do
  sleep 1
done
echo "MongoDB is ready!"

# Initialize MongoDB with the init script (if it exists)
if [ -f "/docker-entrypoint-initdb.d/init-mongo.js" ]; then
  echo "Initializing MongoDB with init-mongo.js..."
  mongosh < /docker-entrypoint-initdb.d/init-mongo.js
else
  echo "Warning: init-mongo.js not found. Skipping initialization."
fi

# Start the Python application using Gunicorn
echo "Starting the Python application..."
exec python3 -m gunicorn rag.com.app:app --bind 0.0.0.0:5000 --workers 4
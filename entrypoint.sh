#!/bin/bash

# Start MongoDB in the background
mongod --fork --logpath /var/log/mongodb/mongod.log

# Wait for MongoDB to be ready
until mongosh --eval "print(\"waited for connection\")" > /dev/null 2>&1; do
  sleep 1
done

# Initialize MongoDB with our script
mongosh < /docker-entrypoint-initdb.d/init-mongo.js

# Start the Python application
exec python3 -m gunicorn --bind 0.0.0.0:5000 rag.com.app:app
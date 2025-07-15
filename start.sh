#!/bin/bash

# Start both FastAPI server and Celery worker in the same container

echo "🚀 Starting AI Agents application..."

# Start Celery worker in the background
echo "📋 Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 3

# Start FastAPI server
echo "🌐 Starting FastAPI server..."
python run.py

# If FastAPI exits, kill Celery worker
kill $CELERY_PID 
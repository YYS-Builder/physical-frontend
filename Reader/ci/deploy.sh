#!/bin/bash

# Exit on error
set -e

echo "Starting deployment..."

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables..."
    source .env
fi

# Check if we're in a production environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Deploying to production..."
    
    # Run database migrations
    echo "Running database migrations..."
    alembic upgrade head
    
    # Install production dependencies
    echo "Installing production dependencies..."
    pip install -r requirements.txt --no-dev
    
    # Start the application
    echo "Starting the application..."
    uvicorn Reader.main:app --host 0.0.0.0 --port 8000 --workers 4
    
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo "Deploying to staging..."
    
    # Run database migrations
    echo "Running database migrations..."
    alembic upgrade head
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Start the application
    echo "Starting the application..."
    uvicorn Reader.main:app --host 0.0.0.0 --port 8000 --reload
    
else
    echo "Unknown environment: $ENVIRONMENT"
    exit 1
fi

echo "Deployment completed successfully!" 
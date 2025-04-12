#!/bin/bash

# Exit on error
set -e

echo "Starting CI/CD pipeline..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
echo "Running tests..."
pytest --cov=Reader tests/ --cov-report=xml

# Run linting
echo "Running linting..."
flake8 Reader/

# Run type checking
echo "Running type checking..."
mypy Reader/

# Run security checks
echo "Running security checks..."
bandit -r Reader/

echo "CI/CD pipeline completed successfully!" 
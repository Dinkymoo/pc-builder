#!/bin/bash
# Script to run the FastAPI backend locally
# Usage: ./scripts/start/start-backend.sh

# Change directory to the backend project
cd "$(dirname "$0")/../../pc-builder/pc-builder-backend" || exit 1

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Preparing image directory..."
# Remove any previously generated images directory to avoid duplicates
rm -rf ../cdn-images
mkdir -p ../cdn-images

echo "Starting FastAPI backend server..."
uvicorn main:app --host 0.0.0.0 --port 8000

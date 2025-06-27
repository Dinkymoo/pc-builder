#!/bin/bash
# Run FastAPI backend from project root
cd pc-builder/pc-builder-backend || exit 1
pip install -r requirements.txt
# Remove any previously generated images directory to avoid duplicates
rm -rf ../cdn-images
mkdir ../cdn-images
uvicorn main:app --host 0.0.0.0 --port 8000

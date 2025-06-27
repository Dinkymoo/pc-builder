#!/bin/sh
# Run the pc-builder-backend Docker image and map port 8000

docker build -t pc-builder-backend .
docker run -p 8000:8000 pc-builder-backend

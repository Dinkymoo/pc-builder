#!/bin/bash
# Script to build and start all components in order for local dev or fresh build
set -e

# Get the parent directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 1. Build and start backend (Docker)
echo "[1/4] Building backend Docker image..."
docker build -t pc-builder-backend ./pc-builder/pc-builder-backend

echo "[2/4] Starting backend container..."
docker stop pc-builder-backend-dev 2>/dev/null || true
docker run --rm -d --name pc-builder-backend-dev --env-file .env -p 8000:8000 pc-builder-backend

# 2. Build frontend (Angular)
echo "[3/4] Building frontend..."
cd pc-builder/pc-builder-app
npm install
npm run build
cd ../..

# 3. Start frontend (dev server)
echo "[4/4] Starting frontend dev server..."
cd pc-builder/pc-builder-app
npm start &
FRONTEND_PID=$!
cd ../..

echo "---"
echo "Backend running in Docker as 'pc-builder-backend-dev' on port 8000."
echo "Frontend running (dev server) on port 4200."
echo "Press Ctrl+C to stop the frontend. To stop backend: docker stop pc-builder-backend-dev"

wait $FRONTEND_PID

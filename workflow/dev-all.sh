#!/bin/bash
# Dev script: build and run all components for local development
set -e

# Get the parent directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 1. Start backend (FastAPI, reload mode)
echo "[1/3] Starting backend (FastAPI)..."
cd pc-builder/pc-builder-backend
if [ ! -d "../.venv" ]; then
  python3 -m venv ../.venv
fi
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload &
BACKEND_PID=$!
cd ../..

# 2. Start frontend (Angular)
echo "[2/3] Starting frontend (Angular)..."
cd pc-builder/pc-builder-app
npm install
npm start &
FRONTEND_PID=$!
cd ../..

# 3. (Optional) Start scraper in watch mode or run once
echo "[3/3] Scraper ready. To run:"
echo "   cd pc-builder/pc-builder-scraper && source ../.venv/bin/activate && python -m scraper.main"

echo "---"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "---"
echo "Both backend and frontend are running in the background."
echo "Press Ctrl+C to stop."

# Wait for background jobs
wait $BACKEND_PID $FRONTEND_PID

#!/bin/bash
# Stop immediately if a command fails; this avoids starting with missing dependencies.
set -e
# Resolve the repository root from this script's location, regardless of the caller's directory.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend/source"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"
# Create the virtual environment only when it does not already exist.
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment in $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
echo "Installing backend dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -r "$BACKEND_DIR/requirements.txt"
# Install frontend packages only when its local dependency directory is absent.
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Installing frontend dependencies..."
  cd "$FRONTEND_DIR"
  npm install
fi
BACKEND_LOG="$ROOT_DIR/backend.log"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
cd "$BACKEND_DIR"
# Make backend modules importable by Python and Uvicorn.
export PYTHONPATH="$BACKEND_DIR"
echo "Starting FastAPI backend..."
# Start Uvicorn with reload enabled and redirect both output streams to its log.
nohup uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
# Save the background backend process ID so cleanup can stop it.
BACKEND_PID=$!
cd "$FRONTEND_DIR"
echo "Starting React frontend..."
# Start Vite on port 5173 and redirect both output streams to its log.
nohup npm run dev -- --host 0.0.0.0 --port 5173 > "$FRONTEND_LOG" 2>&1 &
# Save the background frontend process ID so cleanup can stop it.
FRONTEND_PID=$!
# Follow both log files and initially print their latest 20 lines.
tail -n 20 -F "$BACKEND_LOG" "$FRONTEND_LOG" &
# Save the log follower's process ID so cleanup can stop it.
TAIL_PID=$!
# Define a cleanup routine for stopping the log follower and both app processes.
cleanup() {
  trap - EXIT INT TERM
  # Let the user know both services are being shut down.
  echo "Stopping services..."
  # Send termination signals to log tailing and both application processes.
  kill "$TAIL_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  # Wait for all background processes to exit; ignore expected termination statuses.
  wait "$TAIL_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
# Run cleanup when the script exits or receives Ctrl+C / a termination signal.
trap cleanup EXIT INT TERM
echo ""
echo "Backend is running at: http://127.0.0.1:8000"
echo "Frontend is running at: http://127.0.0.1:5173"
echo "Following logs (Ctrl+C stops both apps):"
echo "  - Backend: $BACKEND_LOG"
echo "  - Frontend: $FRONTEND_LOG"
# Wait for background jobs; the EXIT/INT/TERM trap handles shutdown.
wait
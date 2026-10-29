#!/bin/bash
set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend/source"
FRONTEND_DIR="$ROOT_DIR/frontend"
VENV_DIR="$ROOT_DIR/.venv"
if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Python environment not found: $VENV_DIR"
  exit 1
fi

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "Frontend dependencies not found. Run 'cd frontend && npm install'."
  exit 1
fi

BACKEND_LOG="$ROOT_DIR/backend.log"
FRONTEND_LOG="$ROOT_DIR/frontend.log"
cd "$BACKEND_DIR"
export PYTHONPATH="$BACKEND_DIR"
echo "Starting backend..."
nohup "$VENV_DIR/bin/python" -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
cd "$FRONTEND_DIR"
echo "Starting frontend..."
nohup npm run dev -- --host 0.0.0.0 --port 5173 > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
tail -n 20 -F "$BACKEND_LOG" "$FRONTEND_LOG" &
TAIL_PID=$!
cleanup() {
  trap - EXIT INT TERM
  echo "Stopping services..."
  kill "$TAIL_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$TAIL_PID" "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
echo ""
echo "Backend is running at: http://127.0.0.1:8000"
echo "Frontend is running at: http://127.0.0.1:5173"
echo "Following logs (Ctrl+C stops both apps):"
echo "  - Backend: $BACKEND_LOG"
echo "  - Frontend: $FRONTEND_LOG"
wait

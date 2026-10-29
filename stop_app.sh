#!/bin/bash

# Stop only processes currently listening on the ports used by this project.
PORTS=(8000 5173)

stopped=false

for port in "${PORTS[@]}"; do
  pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)

  if [ -n "$pids" ]; then
    stopped=true
    echo "Stopping processes on port $port: $pids"
    kill $pids 2>/dev/null || true
  else
    echo "No process is listening on port $port"
  fi
done

# Wait briefly, then force-stop only still-running listeners if they ignored SIGTERM.
sleep 2
for port in "${PORTS[@]}"; do
  pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "Force stopping processes on port $port: $pids"
    kill -9 $pids 2>/dev/null || true
  fi
done

if [ "$stopped" = true ]; then
  echo "RAG chatbot stopped."
else
  echo "RAG chatbot was already stopped."
fi

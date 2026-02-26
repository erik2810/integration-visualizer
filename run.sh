#!/bin/bash
set -e

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "No venv found — run setup.sh first."
    echo "Trying system Python..."
fi

# Load .env
if [ -f ".env" ]; then
    set -a; source .env; set +a
fi

# Backend
cd "$(dirname "$0")"
python -m uvicorn backend.app:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000} --reload &
BACKEND_PID=$!
sleep 2

# Frontend
npm run dev &
FRONTEND_PID=$!

echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:${APP_PORT:-8000}"
echo "Ctrl+C to stop"

cleanup() {
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM
wait

#!/bin/bash
set -e

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. https://www.python.org/downloads/"
    exit 1
fi
echo "Python: $(python3 --version 2>&1 | awk '{print $2}')"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js is required. https://nodejs.org/"
    exit 1
fi
echo "Node: $(node --version)"

# Python venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created venv"
fi
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt

# Node deps
npm install

# .env
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

echo ""
echo "Done. Run ./run.sh to start."

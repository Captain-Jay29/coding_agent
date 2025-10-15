#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")/../.."

# Activate venv
source venv/bin/activate

# Start the server
echo "🚀 Starting backend server on http://localhost:8000"
echo "📝 API Docs: http://localhost:8000/docs"
echo ""
python web_ui/backend/server.py


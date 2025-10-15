#!/bin/bash

# Navigate to frontend directory
cd "$(dirname "$0")"

echo "🚀 Starting frontend on http://localhost:3000"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Start the dev server
npm run dev


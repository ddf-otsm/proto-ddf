#!/bin/bash

echo "🚀 Starting my news website..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! pip show reflex > /dev/null 2>&1; then
    echo "📥 Installing dependencies..."
    pip install -q -r requirements.txt
fi

echo "✨ App will be available at:"
echo "   Frontend: http://localhost:4393"
echo "   Backend:  http://localhost:4392"
echo ""

# Run the app
reflex run

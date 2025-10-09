#!/bin/bash

# Proto DDF - Run Script
# This script sets up and runs the Reflex application

echo "🚀 Starting Proto DDF Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/pyvenv.cfg" ] || ! pip show reflex > /dev/null 2>&1; then
    echo "📥 Installing dependencies..."
    pip install reflex
fi

# Initialize submodules if needed
if [ ! -d "reflex" ]; then
    echo "🔗 Initializing submodules..."
    git submodule update --init --recursive
fi

# Run the application
echo "🌟 Starting Reflex application..."
echo "   Open your browser to: http://localhost:3000"
echo "   Press Ctrl+C to stop the server"
echo ""

reflex run

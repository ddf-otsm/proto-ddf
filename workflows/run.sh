#!/bin/bash

# NetSuite Integration Hub - Run Script
# This script sets up and runs the Reflex application

echo "🔄 Starting NetSuite Integration Hub..."

# Check Python version FIRST before creating venv
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

echo "   Found: Python $PYTHON_VERSION"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo ""
    echo "❌ ERROR: Python $REQUIRED_VERSION or higher is required"
    echo "   Current version: Python $PYTHON_VERSION"
    echo ""
    echo "📝 How to fix:"
    echo ""
    echo "   macOS:"
    echo "     brew install python@3.10"
    echo "     # Then use: python3.10 -m venv venv"
    echo ""
    echo "   Ubuntu/Debian:"
    echo "     sudo apt install python3.10 python3.10-venv"
    echo "     # Then use: python3.10 -m venv venv"
    echo ""
    echo "   Or download from: https://www.python.org/downloads/"
    echo ""
    echo "   After installing Python 3.10+, delete the venv folder and run this script again:"
    echo "     rm -rf venv && ./run.sh"
    echo ""
    exit 1
fi

# Initialize submodules if needed
if [ ! -f "reflex/pyproject.toml" ]; then
    echo "🔗 Initializing reflex submodule..."
    git submodule update --init --recursive
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with Python $PYTHON_VERSION..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed (including reflex from submodule)
if [ ! -f "venv/pyvenv.cfg" ] || ! pip show reflex > /dev/null 2>&1; then
    echo "📥 Installing dependencies..."
    echo "   Upgrading pip and build tools..."
    pip install -q --upgrade pip setuptools wheel
    echo "   Installing reflex from submodule..."
    pip install -q -e ./reflex
    echo "   Installing other requirements (if any)..."
    pip install -q -r requirements.txt 2>/dev/null || true
fi

# Get the machine's IP address
if command -v ipconfig &> /dev/null; then
    # macOS
    IP_ADDR=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")
elif command -v hostname &> /dev/null; then
    # Linux
    IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
else
    IP_ADDR="127.0.0.1"
fi

# Retrieve dynamically assigned ports from centralized configuration
# Ports are randomly selected (3000-5000) and persisted in config/.port_config.json
FRONTEND_PORT=$(python3 -c "from config.constants import FRONTEND_PORT; print(FRONTEND_PORT)" 2>/dev/null || echo "3797")
BACKEND_PORT=$(python3 -c "from config.constants import BACKEND_PORT; print(BACKEND_PORT)" 2>/dev/null || echo "3539")

# Display application startup information
echo "🌟 Starting Proto-DDF Generator Interface..."
echo ""
echo "   📱 Generator Interface:"
echo "      Local:    http://127.0.0.1:${FRONTEND_PORT}"
echo "      Network:  http://${IP_ADDR}:${FRONTEND_PORT}"
echo ""
echo "   🔌 Backend API:"
echo "      http://0.0.0.0:${BACKEND_PORT}"
echo ""
echo "   📂 Generated apps are located in: generated/"
echo "   🎯 Ports are randomly assigned (3000-5000) and saved in config/.port_config.json"
echo "   🔧 To run generated apps: cd generated/<app_name> && ./run.sh"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Launch the Proto-DDF generator application
reflex run

#!/bin/bash

# NetSuite Integration Hub - Run Script
# This script sets up and runs the Reflex application

# Parse command line arguments
PARAMS=""
while (( "$#" )); do
  case "$1" in
    -p1|--param1)
      if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
        PARAM1="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    -p2|--param2)
      if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
        PARAM2="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --param1=*)
      PARAM1="${1#*=}"
      shift 1
      ;;
    --param2=*)
      PARAM2="${1#*=}"
      shift 1
      ;;
    --log=*)
      LOG_LEVEL="${1#*=}"
      shift 1
      ;;
    -l|--log)
      if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
        LOG_LEVEL="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      echo "Usage: $0 [--param1=value1] [-p1 value1] [--param2=value2] [-p2 value2] [--log=LEVEL] [-l LEVEL]"
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

# Display ASCII header with parameters
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                            🚀 PROTO-DDF 🚀                                ║"
echo "║                       Reflex Application Generator                        ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
if [ -n "$PARAM1" ] || [ -n "$PARAM2" ] || [ -n "$LOG_LEVEL" ]; then
    echo "║ PARAMETERS:                                                              ║"
    [ -n "$PARAM1" ] && printf "║   param1: %-60s ║\\n" "$PARAM1"
    [ -n "$PARAM2" ] && printf "║   param2: %-60s ║\\n" "$PARAM2"
    [ -n "$LOG_LEVEL" ] && printf "║   log: %-64s ║\\n" "$LOG_LEVEL"
    echo "╠══════════════════════════════════════════════════════════════════════════════╣"
else
    echo "║ No custom parameters specified                                           ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════╣"
fi
echo "║ Starting NetSuite Integration Hub...                                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Set default log level if not specified
if [ -z "$LOG_LEVEL" ]; then
    LOG_LEVEL="ERROR"
fi

# Determine the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if we're already in the project root (called from Makefile)
if [ -f "rxconfig.py" ] && [ -f "Makefile" ]; then
    PROJECT_ROOT="$(pwd)"
fi

# Change to project root
cd "$PROJECT_ROOT" || exit 1

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
# shellcheck disable=SC1091
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
FRONTEND_PORT=$(python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from config.constants import FRONTEND_PORT
print(FRONTEND_PORT)
" 2>/dev/null || python3 -c "
import random
import socket
import json
from pathlib import Path

def is_port_available(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

# Try to find an available port in range
for _ in range(100):
    port = random.randint(3000, 5000)
    if is_port_available(port):
        print(port)
        break
else:
    print('3797')  # fallback
" 2>/dev/null || echo "3797")

BACKEND_PORT=$(python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from config.constants import BACKEND_PORT
print(BACKEND_PORT)
" 2>/dev/null || python3 -c "
import random
import socket

def is_port_available(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

# Try to find an available port in range, different from frontend
frontend_port = int('$FRONTEND_PORT')
for _ in range(100):
    port = random.randint(3000, 5000)
    if port != frontend_port and is_port_available(port):
        print(port)
        break
else:
    print('3539')  # fallback
" 2>/dev/null || echo "3539")

# Display application startup information and run
(
    echo "🌟 Starting Proto-DDF Generator Interface..."
    echo ""
    # ASCII footer with all serving URLs
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                              🌐 SERVING URLS 🌐                             ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════╣"
    echo "║ 🎨 PROTO-DDF GENERATOR:                                                     ║"
    printf "║   Frontend: http://127.0.0.1:%-45s ║\\n" "${FRONTEND_PORT}"
    printf "║   Network:  http://%s:%-45s ║\\n" "${IP_ADDR}" "${FRONTEND_PORT}"
    echo "║                                                                            ║"
    echo "║ 🔧 BACKEND API:                                                            ║"
    printf "║   API:      http://0.0.0.0:%-45s ║\\n" "${BACKEND_PORT}"
    echo "║                                                                            ║"
    echo "║ 📱 GENERATED APPLICATIONS:                                                 ║"
    echo "║   Location: generated/                                                     ║"
    echo "║   Command:  cd generated/<app_name> && ./run.sh                           ║"
    echo "║                                                                            ║"
    echo "║ 📊 PORT CONFIGURATION:                                                     ║"
    echo "║   File:     config/.port_config.json                                       ║"
    echo "║   Range:    3000-5000 (randomly assigned)                                  ║"
    echo "║                                                                            ║"
    echo "║ 🛑 TO STOP: Press Ctrl+C                                                   ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""

    # Check Node.js version for Reflex compatibility
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | sed 's/^v//' | cut -d'.' -f1)
        MIN_VERSION=20
        if [ "$NODE_VERSION" -lt "$MIN_VERSION" ]; then
            echo "⚠️  Node.js version v${NODE_VERSION}.* detected. Reflex recommends >= ${MIN_VERSION}.19.0 for best compatibility."
            echo "   To upgrade (if using nvm): nvm install ${MIN_VERSION} && nvm use ${MIN_VERSION} && nvm alias default ${MIN_VERSION}"
            echo "   The app will still run, but some features may be limited."
        else
            echo "✅ Node.js version v${NODE_VERSION}.* is compatible."
        fi
    fi

    # Clean up any lingering processes on common ports to avoid binding conflicts
    if [ -f "./cleanup_ports.sh" ]; then
        echo "🧹 Running port cleanup to free up any bound ports..."
        ./cleanup_ports.sh
    else
        echo "ℹ️  cleanup_ports.sh not found; skipping port cleanup."
    fi

    # Launch the Proto-DDF generator application
    reflex run
)

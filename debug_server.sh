#!/bin/bash

# Debug Server Script for NetSuite Integration Hub
# This script runs the server with maximum debugging information

echo "🐛 Starting NetSuite Integration Hub in DEBUG mode..."
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run ./run.sh first."
    exit 1
fi

# Clear old logs
echo "📝 Clearing old log files..."
rm -f proto_ddf.log integration_hub.log

# Set debug environment variables
export REFLEX_LOGLEVEL=debug
export PYTHONUNBUFFERED=1

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

echo ""
echo "🌟 Starting Reflex in DEBUG mode..."
echo ""
echo "   📱 Access URLs:"
echo "      Local:    http://127.0.0.1:3000"
echo "      Network:  http://${IP_ADDR}:3000"
echo ""
echo "   🔌 Backend API:"
echo "      http://0.0.0.0:8000"
echo ""
echo "   📋 Log Files:"
echo "      proto_ddf.log         - Configuration & framework logs"
echo "      integration_hub.log   - Application & state logs"
echo ""
echo "   💡 Monitor logs in another terminal:"
echo "      tail -f proto_ddf.log integration_hub.log"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Run reflex with debug logging
reflex run --loglevel debug 2>&1 | tee debug_output.log

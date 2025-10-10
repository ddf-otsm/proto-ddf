#!/bin/bash
#
# NetSuite Integration Hub - Generated App Runner
# ================================================
#
# This script runs the NetSuite Integration Hub application that was generated
# by Proto-DDF. It demonstrates multi-source data integration capabilities.
#
# The app provides:
# - 6 data source types: CSV, JSON, Database, REST API, Salesforce, Webhook
# - Real-time sync with progress tracking and error handling
# - Intelligent field mapping between sources and NetSuite
# - Statistics dashboard with sync metrics
# - Integration logs with timestamps
#
# Usage: ./run.sh (from generated/netsuite_integration_hub/ directory)
#

echo "🔄 Starting NetSuite Integration Hub..."

# Navigate to app directory and locate project root
cd "$(dirname "$0")"
PROJECT_ROOT="$(cd ../.. && pwd)"

# Verify the parent project's virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ ERROR: Virtual environment not found at $PROJECT_ROOT/venv"
    echo "   Please run ./run.sh from the project root first to set up the environment"
    exit 1
fi

echo "🔧 Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Retrieve dynamically assigned ports from centralized configuration
# Ports are randomly selected (3000-5000) and persisted in config/.port_config.json
FRONTEND_PORT=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from config.constants import FRONTEND_PORT; print(FRONTEND_PORT)" 2>/dev/null || echo "3797")
BACKEND_PORT=$(python3 -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); from config.constants import BACKEND_PORT; print(BACKEND_PORT)" 2>/dev/null || echo "3539")

# Determine network interface address for external access
if command -v ipconfig &> /dev/null; then
    # macOS: Get IP address from active network interface
    IP_ADDR=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")
elif command -v hostname &> /dev/null; then
    # Linux: Get IP address from hostname command
    IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "127.0.0.1")
else
    # Fallback to loopback interface
    IP_ADDR="127.0.0.1"
fi

# Display application startup information
echo "🌟 Starting NetSuite Integration Hub..."
echo ""
echo "   📱 Application Interface:"
echo "      Local:    http://127.0.0.1:${FRONTEND_PORT}"
echo "      Network:  http://${IP_ADDR}:${FRONTEND_PORT}"
echo ""
echo "   🔌 Backend API:"
echo "      http://0.0.0.0:${BACKEND_PORT}"
echo ""
echo "   📊 Features:"
echo "      • 6 data source types (CSV, JSON, Database, REST API, Salesforce, Webhook)"
echo "      • Real-time sync with progress tracking"
echo "      • Intelligent field mapping"
echo "      • Statistics dashboard"
echo "      • Integration logs with timestamps"
echo ""
echo "   🎯 Ports are randomly assigned (3000-5000) and persisted in config/"
echo "   Press Ctrl+C to stop the server"
echo ""

# Launch the Reflex application
reflex run


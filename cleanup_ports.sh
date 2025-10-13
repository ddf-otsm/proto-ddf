#!/bin/bash

# Proto-DDF Port Cleanup Script
# This script kills any leftover processes on ports used by the application

echo "🧹 Cleaning up Proto-DDF ports..."

# Check if config file exists
CONFIG_FILE="config/.port_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

# Extract ports from config
BACKEND_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('backend', '3539'))" 2>/dev/null || echo "3539")
FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('frontend', '3797'))" 2>/dev/null || echo "3797")
GENERATED_BACKEND_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('generated_backend', '4984'))" 2>/dev/null || echo "4984")
GENERATED_FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('generated_frontend', '3459'))" 2>/dev/null || echo "3459")

echo "🔍 Checking ports: backend=$BACKEND_PORT, frontend=$FRONTEND_PORT, gen_backend=$GENERATED_BACKEND_PORT, gen_frontend=$GENERATED_FRONTEND_PORT"

# Function to kill processes on a port
kill_port_processes() {
    local port=$1
    local port_name=$2

    # Get PIDs listening on the port
    PIDS=$(lsof -ti :$port 2>/dev/null)

    if [ -n "$PIDS" ]; then
        echo "🔪 Killing processes on port $port ($port_name): $PIDS"
        kill -9 $PIDS 2>/dev/null
        sleep 1

        # Check if still running
        if lsof -ti :$port >/dev/null 2>&1; then
            echo "⚠️  Some processes may still be running on port $port"
        else
            echo "✅ Port $port ($port_name) is now free"
        fi
    else
        echo "✅ Port $port ($port_name) is already free"
    fi
}

# Kill processes on all ports
kill_port_processes $BACKEND_PORT "generator-backend"
kill_port_processes $FRONTEND_PORT "generator-frontend"
kill_port_processes $GENERATED_BACKEND_PORT "generated-app-backend"
kill_port_processes $GENERATED_FRONTEND_PORT "generated-app-frontend"

echo ""
echo "🎉 Port cleanup complete!"
echo "💡 You can now run: ./run.sh"

#!/bin/bash

# Script to run Playwright E2E tests

set -e  # Exit on error

echo "🎭 Running Proto-DDF E2E Tests"
echo "==============================="
echo ""

# Parse command line arguments
HEADED=""
BROWSER="chromium"
TEST_FILE=""
SLOWMO=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            HEADED="--headed"
            shift
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --slowmo)
            SLOWMO="--slowmo $2"
            shift 2
            ;;
        --file)
            TEST_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--headed] [--browser chromium|firefox|webkit] [--slowmo MS] [--file TEST_FILE]"
            exit 1
            ;;
    esac
done

# Check if Playwright is installed
if ! command -v playwright &> /dev/null; then
    echo "❌ Playwright not found. Please run: ./scripts/setup_e2e_tests.sh"
    exit 1
fi

# Check port configuration
if [ ! -f "config/.port_config.json" ]; then
    echo "⚠️  Port configuration not found"
    echo "   Please run 'reflex run' once to generate port configuration"
    exit 1
fi

# Read ports from config
FRONTEND_PORT=$(python3 -c "import json; print(json.load(open('config/.port_config.json'))['frontend'])")
echo "📊 Port configuration:"
echo "   Frontend: $FRONTEND_PORT"
echo ""

# Check if server is running
echo "🔍 Checking if Reflex server is running..."
if ! curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
    echo "❌ Reflex server is not running on port $FRONTEND_PORT"
    echo ""
    echo "Please start the server in another terminal:"
    echo "   reflex run"
    echo ""
    exit 1
fi
echo "✅ Server is running"
echo ""

# Determine test path
if [ -n "$TEST_FILE" ]; then
    TEST_PATH="tests/e2e/$TEST_FILE"
else
    TEST_PATH="tests/e2e/"
fi

# Run tests
echo "🧪 Running tests from: $TEST_PATH"
echo "   Browser: $BROWSER"
if [ -n "$HEADED" ]; then
    echo "   Mode: Headed (browser visible)"
else
    echo "   Mode: Headless"
fi
echo ""

pytest "$TEST_PATH" \
    -v \
    --browser "$BROWSER" \
    $HEADED \
    "$SLOWMO" \
    --html=test-report.html \
    --self-contained-html

echo ""
echo "✅ Tests complete!"
echo "   Report: test-report.html"
echo ""

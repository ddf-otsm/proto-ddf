#!/bin/bash

echo "🎭 Running Playwright Tests with Inspector (Dev Tools)"
echo "========================================================"
echo ""

# Check if server is running
PORT=4692
if ! lsof -ti:$PORT > /dev/null 2>&1; then
    echo "❌ Server is not running on port $PORT"
    echo ""
    echo "Please start the server first:"
    echo "   Terminal 1: reflex run"
    echo ""
    echo "Then run this script again in Terminal 2."
    exit 1
fi

echo "✅ Server is running on port $PORT"
echo ""
echo "Opening Playwright Inspector (Browser + Dev Tools)..."
echo ""
echo "You will see:"
echo "  1. A browser window with your app"
echo "  2. Playwright Inspector panel (dev tools)"
echo "  3. Step-through controls"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run test with Playwright Inspector
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage::test_page_loads -v

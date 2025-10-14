#!/bin/bash
# COPY AND PASTE THIS ENTIRE SCRIPT INTO YOUR TERMINAL

echo "🎭 Playwright E2E Test - Browser + Dev Tools"
echo "=============================================="
echo ""

# Check if in correct directory
if [ ! -f "rxconfig.py" ]; then
    echo "❌ Wrong directory! Please run:"
    echo "   cd /Users/luismartins/local_repos/proto-ddf"
    echo "   Then run this script again."
    exit 1
fi

# Check if server is running
if ! lsof -ti:4692 > /dev/null 2>&1; then
    echo "❌ Server NOT running!"
    echo ""
    echo "Please start the server first:"
    echo "   1. Open a NEW terminal"
    echo "   2. Run: cd /Users/luismartins/local_repos/proto-ddf"
    echo "   3. Run: reflex run"
    echo "   4. Wait for: 'App running at: http://0.0.0.0:4692'"
    echo "   5. Come back here and run this script again"
    echo ""
    exit 1
fi

echo "✅ Server is running!"
echo ""
echo "🌐 Opening Browser + Playwright Inspector (Dev Tools)..."
echo ""
echo "You will see:"
echo "  1. Chrome browser window with your app"
echo "  2. Playwright Inspector panel (your dev tools)"
echo "  3. Step-through controls"
echo ""
echo "Use the Inspector to:"
echo "  • Click 'Resume' or 'Step Over' to proceed"
echo "  • Inspect elements"
echo "  • View console logs"
echo "  • Check network requests"
echo ""
echo "Starting in 3 seconds..."
sleep 3

# Run test with Playwright Inspector (Browser + Dev Tools)
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage::test_page_loads -v

echo ""
echo "✅ Test complete!"
echo ""
echo "To run more tests with Browser + Dev Tools:"
echo "   PWDEBUG=1 pytest tests/e2e/test_generator_app.py -v"
echo ""

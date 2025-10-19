#!/bin/bash

################################################################################
#                     PROTO-DDF E2E TEST RUNNER
################################################################################
#
# NAME
#   run_e2e_tests.sh - Run end-to-end tests using Playwright
#
# SYNOPSIS
#   ./scripts/run_e2e_tests.sh [OPTIONS]
#
# DESCRIPTION
#   This script runs end-to-end tests against the Proto-DDF application
#   using Playwright for browser automation. Validates the complete user
#   workflow from application start through generating and managing apps.
#
#   Features:
#   - Multiple browser support (chromium, firefox, webkit)
#   - Headed and headless modes
#   - Slowed execution for debugging (--slowmo)
#   - Single test file or full suite execution
#   - HTML test report generation
#   - Automatic server health check
#
# USAGE
#   ./scripts/run_e2e_tests.sh                 # Run all tests (headless)
#   ./scripts/run_e2e_tests.sh --headed        # Run with browser visible
#   ./scripts/run_e2e_tests.sh --browser firefox  # Use Firefox
#   ./scripts/run_e2e_tests.sh --slowmo 1000   # 1 second delay between actions
#   ./scripts/run_e2e_tests.sh --file test_ui.py  # Single test file
#   ./scripts/run_e2e_tests.sh --help          # Show help
#
# OPTIONS
#   --headed              Run tests with browser window visible
#   --browser BROWSER     Browser engine to use (default: chromium)
#                        Options: chromium, firefox, webkit
#   --slowmo MS           Slow down test execution by MS milliseconds
#                        Useful for debugging slow interactions
#   --file TEST_FILE      Run specific test file (relative to tests/e2e/)
#   --help, -h            Display this help message
#
# ENVIRONMENT
#   HEADLESS_MODE         Set to true for headless operation (default: true)
#   BROWSER               Browser engine to use (default: chromium)
#   SLOWMO                Milliseconds to slow down (default: 0)
#   TEST_FILE             Specific test file to run (default: all)
#   FRONTEND_PORT         Port where Reflex frontend is running (auto-detected)
#
# EXIT CODES
#   0 - All tests passed
#   1 - Playwright not installed
#   2 - Port configuration not found
#   3 - Server not running on configured port
#   4 - Tests failed (see report for details)
#   5 - Invalid command line arguments
#
# FILES
#   tests/e2e/            - Test files directory
#   test-report.html      - Generated test report (in project root)
#   config/.port_config.json  - Port configuration
#
# EXAMPLES
#   # Run all tests headless (CI/CD)
#   ./scripts/run_e2e_tests.sh
#
#   # Run with visible browser for debugging
#   ./scripts/run_e2e_tests.sh --headed
#
#   # Run slow tests with Firefox
#   ./scripts/run_e2e_tests.sh --browser firefox --slowmo 500
#
#   # Run specific test file
#   ./scripts/run_e2e_tests.sh --file test_generator_ui.py
#
# TEST SUITE
#   The test suite validates:
#   - Application loads correctly
#   - UI components render properly
#   - Application generation workflow
#   - Generated app management (open, stop, restart)
#   - Port management and conflict handling
#   - Error handling and recovery
#
# REQUIREMENTS
#   - Python 3.10+
#   - pytest and pytest-playwright
#   - Playwright browsers installed (chromium, firefox, webkit)
#   - Proto-DDF generator running (reflex run)
#   - curl utility (for server health check)
#
# NOTES
#   - Requires Reflex server running on configured port
#   - Tests may take 30-60 seconds depending on complexity
#   - HTML report useful for debugging failed tests
#   - Headed mode useful for interactive debugging
#   - Slowmo recommended for troubleshooting flaky tests
#
# PREREQUISITES
#   1. Install test dependencies:
#      pip install -r requirements.txt
#
#   2. Ensure Reflex is running:
#      ./run.sh
#
#   3. Run the tests:
#      ./scripts/run_e2e_tests.sh
#
# SEE ALSO
#   ./run.sh              - Start the application
#   ./cleanup_ports.sh    - Free up ports if tests fail
#   tests/unit/           - Unit tests
#
# AUTHOR
#   Proto-DDF Development Team
#
################################################################################

set -e  # Exit on error (unless caught)

# Configuration
HEADED=""
BROWSER="chromium"
TEST_FILE=""
SLOWMO=""
EXIT_CODE=0

################################################################################
# LOGGING FUNCTIONS
################################################################################

log_info() {
    echo "ℹ️  $1" >&2
}

log_success() {
    echo "✅ $1" >&2
}

log_warning() {
    echo "⚠️  WARNING: $1" >&2
}

log_error() {
    echo "❌ ERROR: $1" >&2
}

log_progress() {
    echo "🔄 $1" >&2
}

log_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║      🎭 PROTO-DDF E2E TEST RUNNER                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

log_footer() {
    echo ""
    if [ "$EXIT_CODE" -eq 0 ]; then
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║      ✅ All tests passed!                                       ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
    else
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║      ❌ Tests failed - see report for details                   ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
    fi
    echo ""
}

show_help() {
    cat << 'EOF'
Usage: ./scripts/run_e2e_tests.sh [OPTIONS]

Run end-to-end tests against Proto-DDF using Playwright.

OPTIONS:
  --headed              Run tests with browser visible
  --browser BROWSER     Browser engine (chromium/firefox/webkit)
  --slowmo MS           Slow down test execution (milliseconds)
  --file TEST_FILE      Run specific test file
  --help, -h            Show this help

EXAMPLES:
  ./scripts/run_e2e_tests.sh              # Run all tests
  ./scripts/run_e2e_tests.sh --headed    # With visible browser
  ./scripts/run_e2e_tests.sh --browser firefox --slowmo 500
  ./scripts/run_e2e_tests.sh --file test_app_generator.py

PREREQUISITES:
  - Reflex running (./run.sh)
  - Playwright installed
  - pytest-playwright installed

For full documentation, see the script header.
EOF
}

################################################################################
# COMMAND LINE PARSING
################################################################################

while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            HEADED="--headed"
            log_progress "Headed mode enabled (browser visible)"
            shift
            ;;
        --browser)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                BROWSER="$2"
                log_progress "Browser set to: $BROWSER"
                shift 2
            else
                log_error "Argument for $1 is missing"
                show_help
                exit 5
            fi
            ;;
        --slowmo)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                SLOWMO="--slowmo $2"
                log_progress "Slowmo set to: $2 ms"
                shift 2
            else
                log_error "Argument for $1 is missing"
                show_help
                exit 5
            fi
            ;;
        --file)
            if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
                TEST_FILE="$2"
                log_progress "Test file set to: $TEST_FILE"
                shift 2
            else
                log_error "Argument for $1 is missing"
                show_help
                exit 5
            fi
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 5
            ;;
    esac
done

################################################################################
# MAIN LOGIC
################################################################################

log_header
log_info "Proto-DDF E2E Test Runner"
echo ""

# Check if Playwright is installed
log_progress "Checking Playwright installation..."
if ! python3 -c "import pytest_playwright" 2>/dev/null; then
    log_error "pytest-playwright not found"
    log_info "Install test dependencies:"
    log_info "  pip install -r requirements.txt"
    exit 1
fi
log_success "Playwright is installed"

# Check port configuration
log_progress "Checking port configuration..."
if [ ! -f "config/.port_config.json" ]; then
    log_error "Port configuration not found"
    log_info "Please run './run.sh' once to generate port configuration"
    exit 2
fi
log_success "Port configuration found"

# Read ports from config
log_progress "Reading port configuration..."
FRONTEND_PORT=$(python3 -c "import json; data=json.load(open('config/.port_config.json')); print(data.get('frontend', '3797'))" 2>/dev/null || echo "3797")
echo "📊 Port configuration:"
echo "   Frontend: $FRONTEND_PORT"
echo ""

# Check if server is running
log_progress "Checking if Reflex server is running..."
if ! timeout 5 curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
    log_error "Reflex server is not running on port $FRONTEND_PORT"
    log_info ""
    log_info "Please start the server in another terminal:"
    log_info "   ./run.sh"
    log_info ""
    exit 3
fi
log_success "Server is running on port $FRONTEND_PORT"
echo ""

# Determine test path
if [ -n "$TEST_FILE" ]; then
    TEST_PATH="tests/e2e/$TEST_FILE"
    log_info "Running specific test: $TEST_FILE"
else
    TEST_PATH="tests/e2e/"
    log_info "Running all tests in tests/e2e/"
fi

# Display configuration
echo ""
echo "📋 Test Configuration:"
echo "   Browser:    $BROWSER"
if [ -n "$HEADED" ]; then
    echo "   Mode:       Headed (browser visible)"
else
    echo "   Mode:       Headless"
fi
if [ -n "$SLOWMO" ]; then
    echo "   Slowmo:     Enabled"
fi
if [ -n "$TEST_FILE" ]; then
    echo "   Test File:  $TEST_FILE"
else
    echo "   Test Suite: All tests"
fi
echo ""

# Run tests
log_progress "Starting test execution..."
echo ""

if ! pytest "$TEST_PATH" \
    -v \
    --browser "$BROWSER" \
    $HEADED \
    $SLOWMO \
    --html=test-report.html \
    --self-contained-html; then
    EXIT_CODE=4
fi

log_footer

if [ -f "test-report.html" ]; then
    log_success "Test report generated: test-report.html"
    log_info "Open in browser to view detailed results"
fi

echo ""

exit $EXIT_CODE

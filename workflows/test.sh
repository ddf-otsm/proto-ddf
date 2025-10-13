#!/bin/bash
#
# Proto-DDF Test Runner
# =====================
#
# Comprehensive test runner for Proto-DDF application generator.
#
# Usage:
#   ./workflows/test.sh              # Run all tests
#   ./workflows/test.sh unit         # Run unit tests only
#   ./workflows/test.sh integration  # Run integration tests only
#   ./workflows/test.sh coverage     # Run tests with coverage report
#
# Test Types:
# - Unit Tests: Individual component testing
# - Integration Tests: Full workflow testing
# - Coverage: Code coverage analysis
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Proto-DDF Test Suite${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ ERROR: Virtual environment not found${NC}"
    echo "   Run ./workflows/run.sh first to set up the environment"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install test dependencies if needed
echo -e "${BLUE}📦 Checking test dependencies...${NC}"
pip install -q pytest pytest-cov coverage 2>/dev/null || true

# Determine test scope
TEST_SCOPE="${1:-all}"

case "$TEST_SCOPE" in
    unit)
        echo -e "${BLUE}🧪 Running unit tests...${NC}"
        echo ""
        python -m pytest tests/unit/ -v --tb=short
        ;;

    integration)
        echo -e "${BLUE}🔗 Running integration tests...${NC}"
        echo ""
        python -m pytest tests/integration/ -v --tb=short
        ;;

    coverage)
        echo -e "${BLUE}📊 Running tests with coverage...${NC}"
        echo ""
        python -m pytest tests/ -v --cov=config --cov=proto_ddf_app --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
        ;;

    all|*)
        echo -e "${BLUE}🧪 Running all tests...${NC}"
        echo ""

        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}   Unit Tests${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        python -m pytest tests/unit/ -v --tb=short || UNIT_FAILED=1

        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}   Integration Tests${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        python -m pytest tests/integration/ -v --tb=short || INTEGRATION_FAILED=1

        echo ""
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${YELLOW}   Test Summary${NC}"
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

        if [ -z "$UNIT_FAILED" ] && [ -z "$INTEGRATION_FAILED" ]; then
            echo -e "${GREEN}✅ All tests passed!${NC}"
            exit 0
        else
            [ ! -z "$UNIT_FAILED" ] && echo -e "${RED}❌ Unit tests failed${NC}"
            [ ! -z "$INTEGRATION_FAILED" ] && echo -e "${RED}❌ Integration tests failed${NC}"
            exit 1
        fi
        ;;
esac

echo ""
echo -e "${GREEN}✅ Tests completed successfully!${NC}"

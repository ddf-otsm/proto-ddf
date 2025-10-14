#!/bin/bash

# Setup script for Playwright E2E tests

set -e  # Exit on error

echo "🎭 Setting up Playwright E2E Tests for Proto-DDF"
echo "================================================"
echo ""

# Check if running in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Not running in a virtual environment"
    echo "   It's recommended to use a virtual environment"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# Install Python dependencies
echo "📦 Installing Python test dependencies..."
pip install -q pytest>=8.4.2
pip install -q pytest-playwright>=0.4.4
pip install -q playwright>=1.40.0
pip install -q pytest-asyncio>=0.23.0
pip install -q pytest-timeout>=2.2.0
pip install -q pytest-html>=4.0.0

echo "✅ Python dependencies installed"
echo ""

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
echo "   This may take a few minutes on first run..."
playwright install chromium
playwright install firefox
playwright install webkit

echo "✅ Playwright browsers installed"
echo ""

# Create screenshots directory
echo "📁 Creating test directories..."
mkdir -p tests/e2e/screenshots
echo "✅ Test directories created"
echo ""

# Check port configuration
echo "🔍 Checking port configuration..."
if [ -f "config/.port_config.json" ]; then
    echo "✅ Port configuration found"
    cat config/.port_config.json
else
    echo "⚠️  Port configuration not found"
    echo "   Run 'reflex run' once to generate port configuration"
fi
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the Reflex server: reflex run"
echo "2. Run E2E tests: pytest tests/e2e/ -v"
echo "3. Run with browser visible: pytest tests/e2e/ -v --headed"
echo ""

#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║           Python 3.10+ Installation Guide                     ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check current Python
echo "🔍 Current Python version:"
python3 --version
echo ""

# Check if Python 3.10+ already available
echo "🔍 Checking for Python 3.10 or higher..."
if command -v python3.10 &> /dev/null; then
    echo "✅ Python 3.10 found!"
    python3.10 --version
    PYTHON_CMD="python3.10"
elif command -v python3.11 &> /dev/null; then
    echo "✅ Python 3.11 found!"
    python3.11 --version
    PYTHON_CMD="python3.11"
elif command -v python3.12 &> /dev/null; then
    echo "✅ Python 3.12 found!"
    python3.12 --version
    PYTHON_CMD="python3.12"
else
    echo "❌ Python 3.10+ not found"
    echo ""
    echo "📥 To install Python 3.10, run ONE of these:"
    echo ""
    echo "Option 1 - Homebrew (Recommended):"
    echo "  brew install python@3.10"
    echo ""
    echo "Option 2 - Homebrew (Latest):"
    echo "  brew install python@3.11"
    echo ""
    echo "Option 3 - Download from python.org:"
    echo "  https://www.python.org/downloads/"
    echo ""
    echo "After installing, run this script again!"
    exit 1
fi

echo ""
echo "✅ Python 3.10+ is available!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps to set up the application:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Remove old virtual environment:"
echo "   rm -rf venv"
echo ""
echo "2. Create new venv with Python 3.10+:"
echo "   $PYTHON_CMD -m venv venv"
echo ""
echo "3. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "4. Upgrade pip:"
echo "   pip install --upgrade pip setuptools wheel"
echo ""
echo "5. Install Reflex from submodule:"
echo "   pip install -e ./reflex"
echo ""
echo "6. Run the application:"
echo "   reflex run"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Would you like to proceed with setup now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting setup..."
    echo ""
    
    echo "📦 Step 1: Removing old venv..."
    rm -rf venv
    
    echo "📦 Step 2: Creating new venv with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    
    echo "🔧 Step 3: Activating venv..."
    source venv/bin/activate
    
    echo "⬆️  Step 4: Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    echo "📥 Step 5: Installing Reflex from submodule..."
    pip install -e ./reflex
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Setup complete!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "To run the application:"
    echo "  source venv/bin/activate"
    echo "  reflex run"
    echo ""
    echo "Or use debug mode:"
    echo "  ./debug_server.sh"
    echo ""
else
    echo ""
    echo "Setup cancelled. Run this script again when ready!"
fi


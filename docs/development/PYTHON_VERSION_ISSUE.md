# Python Version Issue - CRITICAL

## ⚠️ Current Problem

Your system has **Python 3.9.6** but Reflex requires **Python 3.10 or higher**.

## 🔍 How to Check Your Python Version

```bash
python3 --version
# Shows: Python 3.9.6  ❌ TOO OLD
```

## ✅ Solution Options

### Option 1: Install Python 3.10+ via Homebrew (Recommended for macOS)

```bash
# Install Python 3.10
brew install python@3.10

# Verify installation
python3.10 --version
# Should show: Python 3.10.x or higher

# Create venv with Python 3.10
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate

# Install reflex
pip install --upgrade pip setuptools wheel
pip install -e ./reflex

# Run the app
reflex run
```

### Option 2: Install Python 3.11 (Latest Stable)

```bash
# Install Python 3.11
brew install python@3.11

# Verify
python3.11 --version

# Create venv
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate

# Install and run
pip install --upgrade pip setuptools wheel
pip install -e ./reflex
reflex run
```

### Option 3: Use pyenv (Python Version Manager)

```bash
# Install pyenv
brew install pyenv

# Install Python 3.10
pyenv install 3.10.13

# Set local version for this project
cd /Users/luismartins/local_repos/proto-ddf
pyenv local 3.10.13

# Verify
python3 --version
# Should now show Python 3.10.13

# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install and run
pip install --upgrade pip setuptools wheel
pip install -e ./reflex
reflex run
```

### Option 4: Download from python.org

1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or 3.11 installer
3. Install it
4. Use the specific version:

```bash
# Find where it installed
which python3.10
# or
which python3.11

# Create venv with that version
rm -rf venv
/usr/local/bin/python3.10 -m venv venv  # adjust path as needed
source venv/bin/activate

# Install and run
pip install --upgrade pip setuptools wheel
pip install -e ./reflex
reflex run
```

## 🚀 Quick Fix Script

Save this as `setup_python310.sh`:

```bash
#!/bin/bash

echo "🔧 Setting up Python 3.10 for NetSuite Integration Hub"
echo ""

# Check if python3.10 is available
if command -v python3.10 &> /dev/null; then
    echo "✅ Found Python 3.10"
    PYTHON_CMD=python3.10
elif command -v python3.11 &> /dev/null; then
    echo "✅ Found Python 3.11"
    PYTHON_CMD=python3.11
else
    echo "❌ Python 3.10+ not found"
    echo ""
    echo "Please install Python 3.10 or higher:"
    echo "  brew install python@3.10"
    echo ""
    exit 1
fi

echo "   Using: $PYTHON_CMD"
$PYTHON_CMD --version

echo ""
echo "📦 Creating virtual environment..."
rm -rf venv
$PYTHON_CMD -m venv venv

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -e ./reflex

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  reflex run"
echo ""
```

Make it executable and run:
```bash
chmod +x setup_python310.sh
./setup_python310.sh
```

## 🔍 Troubleshooting

### After Installing Python 3.10, `python3` Still Shows 3.9

This is normal. Use the specific version command:

```bash
# Don't use python3 (still points to 3.9)
python3 --version  # Still 3.9.6

# Use python3.10 specifically
python3.10 --version  # Shows 3.10.x ✅
```

### Make python3.10 the Default (Optional)

```bash
# Create an alias in your shell config (~/.zshrc or ~/.bashrc)
echo 'alias python3=python3.10' >> ~/.zshrc
source ~/.zshrc
```

### Multiple Python Versions

Use pyenv to manage multiple versions:

```bash
brew install pyenv

# Add to ~/.zshrc:
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Install and use Python 3.10
pyenv install 3.10.13
pyenv local 3.10.13  # Sets for current directory
```

## 📝 Why This Happens

The worker crashes you saw (`[ERROR] Unexpected exit from worker-1`) were caused by:

1. Your venv was created with Python 3.9
2. Reflex submodule requires Python 3.10+ (uses Python 3.10+ features)
3. When workers try to start, they fail due to missing Python features
4. Workers crash without clear error messages

## ✅ After Fixing

Once you have Python 3.10+ installed and the venv recreated:

```bash
# Test that it works
source venv/bin/activate
python3 -c "import reflex as rx; print(f'✅ Reflex {rx.__version__}')"

# Run the app
reflex run

# Or use debug mode
./debug_server.sh
```

You should see:
```
App running at: http://localhost:3000/
Backend running at: http://0.0.0.0:8000
```

WITHOUT the worker errors!

## 🎯 Summary

**Problem**: Python 3.9 → Workers crash  
**Solution**: Python 3.10+ → Workers work  

**Quick Fix**:
```bash
brew install python@3.10
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ./reflex
reflex run
```

---

**Need help?** Check [DEBUGGING.md](DEBUGGING.md) for detailed debugging steps.



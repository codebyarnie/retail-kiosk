#!/usr/bin/env bash
#
# Backend installation and verification script
#
# This script installs all backend dependencies and verifies the installation.
#
# Usage:
#   cd backend
#   bash install_and_verify.sh
#
# Or make it executable:
#   chmod +x install_and_verify.sh
#   ./install_and_verify.sh

set -e  # Exit on error

echo "====================================================================="
echo "Backend Installation and Verification"
echo "====================================================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    echo "Please run this script from the backend/ directory."
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python not found in PATH."
    echo "Please install Python 3.11 or higher."
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# Check Python version (should be 3.11+)
echo "Checking Python version..."
$PYTHON_CMD -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; print('✓ Python version OK')"
echo ""

# Install dependencies
echo "Installing backend dependencies..."
echo "This may take a few minutes..."
echo ""

$PYTHON_CMD -m pip install --upgrade pip setuptools wheel
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed successfully!"
echo ""

# Run verification script
echo "Running verification checks..."
echo ""

$PYTHON_CMD verify_installation.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "====================================================================="
    echo "✅ Backend installation and verification COMPLETED!"
    echo "====================================================================="
    echo ""
    echo "Next steps:"
    echo "  1. Copy .env.example to .env and configure environment variables"
    echo "  2. Start the development server: uvicorn app.main:app --reload"
    echo "  3. Visit http://localhost:8000/api/docs for API documentation"
    echo ""
    exit 0
else
    echo ""
    echo "====================================================================="
    echo "❌ Backend verification FAILED!"
    echo "====================================================================="
    echo ""
    echo "Please review the errors above and fix any issues."
    echo ""
    exit 1
fi

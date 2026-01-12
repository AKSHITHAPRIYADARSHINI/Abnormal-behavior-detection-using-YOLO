#!/bin/bash

# Local development startup script for Linux/Mac

echo "========================================"
echo "YOLO Abnormality Detection - Local Run"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not available"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Python version: $PYTHON_VERSION"
echo

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error installing dependencies"
    exit 1
fi

echo
echo "========================================"
echo "Dependencies installed successfully"
echo "========================================"
echo
echo "Starting Flask application..."
echo "Server will be available at: http://localhost:5000"
echo
echo "Press Ctrl+C to stop the server"
echo

export FLASK_ENV=development
python3 app.py

#!/bin/bash
# MiniGridGame Startup Script for Mac/Linux
# This script sets up the environment and runs the application

echo "Starting MiniGridGame setup..."
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        echo "Please ensure Python 3.11+ is installed"
        exit 1
    fi
    echo "Virtual environment created successfully!"
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Install/update requirements
echo "Installing dependencies..."
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements"
    exit 1
fi
echo

# Change to backend directory and run the application
echo "Starting application..."
echo "The app will be available at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo
cd backend
python app.py

@echo off
REM MiniGridGame Startup Script for Windows
REM This script sets up the environment and runs the application

echo Starting MiniGridGame setup...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        echo Please ensure Python 3.11+ is installed
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/update requirements
echo Installing dependencies...
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    pause
    exit /b 1
)
echo.

REM Change to backend directory and run the application
echo Starting application...
echo The app will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
cd backend
python app.py

REM If app exits, pause to see any error messages
pause

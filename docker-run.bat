@echo off
REM Docker Run Script for Neural Navigator (Windows)
REM This script makes it easy to build and run the app with Docker

echo ================================
echo Neural Navigator - Docker Runner
echo ================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed!
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker is ready!
echo.

REM Build the Docker image
echo Building Docker image...
docker build -t neural-navigator .

if errorlevel 1 (
    echo Docker build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo.

REM Run the container
echo Starting Neural Navigator...
docker run -d ^
    --name neural-navigator ^
    -p 5000:8080 ^
    -v "%cd%/backend/static:/app/backend/static" ^
    -e FLASK_ENV=development ^
    -e SECRET_KEY=dev-secret-key ^
    neural-navigator

if errorlevel 1 (
    echo Failed to start container!
    echo It might already be running. Try: docker stop neural-navigator && docker rm neural-navigator
    pause
    exit /b 1
)

echo.
echo Neural Navigator is running!
echo.
echo Access the app at: http://localhost:5000
echo.
echo Useful commands:
echo    View logs:     docker logs -f neural-navigator
echo    Stop app:      docker stop neural-navigator
echo    Remove app:    docker rm neural-navigator
echo    Restart app:   docker restart neural-navigator
echo.
pause

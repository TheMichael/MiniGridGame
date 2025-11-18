@echo off
REM Push Docker Image to Docker Hub (Windows)
REM This makes it easy to deploy to any Docker hosting platform

echo =========================================
echo Neural Navigator - Docker Hub Push Script
echo =========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Get Docker Hub username
set /p DOCKER_USERNAME="Enter your Docker Hub username: "

if "%DOCKER_USERNAME%"=="" (
    echo Username is required!
    pause
    exit /b 1
)

echo.
echo Building Docker image...
docker build -t neural-navigator .

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Tagging image as %DOCKER_USERNAME%/neural-navigator:latest
docker tag neural-navigator %DOCKER_USERNAME%/neural-navigator:latest

echo.
echo Logging in to Docker Hub...
echo Please enter your Docker Hub password/token:
docker login -u %DOCKER_USERNAME%

if errorlevel 1 (
    echo Login failed!
    pause
    exit /b 1
)

echo.
echo Pushing to Docker Hub...
docker push %DOCKER_USERNAME%/neural-navigator:latest

if errorlevel 1 (
    echo Push failed!
    pause
    exit /b 1
)

echo.
echo Successfully pushed to Docker Hub!
echo.
echo Your image is now available at:
echo    docker pull %DOCKER_USERNAME%/neural-navigator:latest
echo.
echo Use this image URL in RunMyDocker or any Docker hosting platform
echo.
pause

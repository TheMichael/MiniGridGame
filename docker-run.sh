#!/bin/bash
# Docker Run Script for Neural Navigator
# This script makes it easy to build and run the app with Docker

echo "🐳 Neural Navigator - Docker Runner"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is ready!"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t neural-navigator .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "✅ Build successful!"
echo ""

# Run the container
echo "🚀 Starting Neural Navigator..."
docker run -d \
    --name neural-navigator \
    -p 5000:8080 \
    -v "$(pwd)/backend/static:/app/backend/static" \
    -e FLASK_ENV=development \
    -e SECRET_KEY=dev-secret-key \
    neural-navigator

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container!"
    echo "It might already be running. Try: docker stop neural-navigator && docker rm neural-navigator"
    exit 1
fi

echo ""
echo "✅ Neural Navigator is running!"
echo ""
echo "🌐 Access the app at: http://localhost:5000"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     docker logs -f neural-navigator"
echo "   Stop app:      docker stop neural-navigator"
echo "   Remove app:    docker rm neural-navigator"
echo "   Restart app:   docker restart neural-navigator"
echo ""

#!/bin/bash
# Push Docker Image to Docker Hub
# This makes it easy to deploy to any Docker hosting platform

echo "🐳 Neural Navigator - Docker Hub Push Script"
echo "==========================================="
echo ""

# Check if Docker is installed and running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Get Docker Hub username
echo "Enter your Docker Hub username:"
read DOCKER_USERNAME

if [ -z "$DOCKER_USERNAME" ]; then
    echo "❌ Username is required!"
    exit 1
fi

echo ""
echo "🔨 Building Docker image..."
docker build -t neural-navigator .

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "🏷️  Tagging image as $DOCKER_USERNAME/neural-navigator:latest"
docker tag neural-navigator $DOCKER_USERNAME/neural-navigator:latest

echo ""
echo "🔐 Logging in to Docker Hub..."
echo "Please enter your Docker Hub password/token:"
docker login -u $DOCKER_USERNAME

if [ $? -ne 0 ]; then
    echo "❌ Login failed!"
    exit 1
fi

echo ""
echo "⬆️  Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/neural-navigator:latest

if [ $? -ne 0 ]; then
    echo "❌ Push failed!"
    exit 1
fi

echo ""
echo "✅ Successfully pushed to Docker Hub!"
echo ""
echo "📦 Your image is now available at:"
echo "   docker pull $DOCKER_USERNAME/neural-navigator:latest"
echo ""
echo "🚀 Use this image URL in RunMyDocker or any Docker hosting platform"
echo ""

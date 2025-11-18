# Docker Setup Guide - Neural Navigator

This guide explains how to run Neural Navigator using Docker.

## Prerequisites

- **Docker Desktop** installed and running
  - Download: https://docs.docker.com/get-docker/
  - Make sure Docker Desktop is started before running any commands

## Quick Start (Easiest)

### Option 1: Using the Automated Scripts

**Mac/Linux:**
```bash
./docker-run.sh
```

**Windows:**
```bash
docker-run.bat
```

The script will:
1. Check if Docker is installed and running
2. Build the Docker image
3. Start the container
4. Show you the URL to access the app

### Option 2: Using Docker Compose

```bash
# Build and start in one command
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build

# Stop when done
docker-compose down
```

### Option 3: Manual Docker Commands

```bash
# 1. Build the image
docker build -t neural-navigator .

# 2. Run the container
docker run -d \
  --name neural-navigator \
  -p 5000:8080 \
  -v "$(pwd)/backend/static:/app/backend/static" \
  -e FLASK_ENV=development \
  neural-navigator

# 3. Access at http://localhost:5000
```

**Windows PowerShell:**
```powershell
docker run -d `
  --name neural-navigator `
  -p 5000:8080 `
  -v "${PWD}/backend/static:/app/backend/static" `
  -e FLASK_ENV=development `
  neural-navigator
```

## Access the Application

Once running, open your browser to:
- **http://localhost:5000**

## Useful Docker Commands

### View Logs
```bash
# Follow logs in real-time
docker logs -f neural-navigator

# View last 100 lines
docker logs --tail 100 neural-navigator
```

### Stop/Start/Restart
```bash
# Stop the container
docker stop neural-navigator

# Start the container
docker start neural-navigator

# Restart the container
docker restart neural-navigator
```

### Remove Container
```bash
# Stop and remove
docker stop neural-navigator
docker rm neural-navigator

# Force remove (if running)
docker rm -f neural-navigator
```

### Rebuild After Code Changes
```bash
# Stop and remove old container
docker stop neural-navigator && docker rm neural-navigator

# Rebuild image
docker build -t neural-navigator .

# Start new container
docker run -d --name neural-navigator -p 5000:8080 neural-navigator
```

Or with Docker Compose:
```bash
docker-compose up --build
```

### Shell Access (Debug)
```bash
# Access bash shell inside container
docker exec -it neural-navigator bash

# Run Python shell
docker exec -it neural-navigator python

# Check files
docker exec -it neural-navigator ls -la /app/backend
```

### View Resource Usage
```bash
# See CPU, memory usage
docker stats neural-navigator

# View all running containers
docker ps

# View all containers (including stopped)
docker ps -a
```

## Environment Variables

You can customize the app with environment variables:

```bash
docker run -d \
  --name neural-navigator \
  -p 5000:8080 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key-here \
  -e PORT=8080 \
  neural-navigator
```

Available variables:
- `FLASK_ENV` - `development` or `production` (default: production)
- `FLASK_HOST` - Host to bind to (default: 0.0.0.0)
- `PORT` - Port inside container (default: 8080)
- `SECRET_KEY` - Flask secret key (default: auto-generated)

## Persistent Data

### Using Volumes

To persist data (database, generated GIFs) across container restarts:

```bash
docker run -d \
  --name neural-navigator \
  -p 5000:8080 \
  -v neural-navigator-data:/app/backend/static \
  -v neural-navigator-db:/app/backend \
  neural-navigator
```

### Using Bind Mounts (Development)

To see live code changes without rebuilding:

```bash
docker run -d \
  --name neural-navigator \
  -p 5000:8080 \
  -v "$(pwd)/backend:/app/backend" \
  neural-navigator
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, map to a different port:
```bash
docker run -d --name neural-navigator -p 8080:8080 neural-navigator
```
Then access at http://localhost:8080

### Container Won't Start
```bash
# Check logs for errors
docker logs neural-navigator

# Check if container exists
docker ps -a

# Remove old container
docker rm neural-navigator
```

### Image Build Fails
```bash
# Clean Docker cache and rebuild
docker builder prune -a
docker build --no-cache -t neural-navigator .
```

### Out of Disk Space
```bash
# Clean up unused images and containers
docker system prune -a

# See disk usage
docker system df
```

### Check Container Health
```bash
# See if container is running
docker ps | grep neural-navigator

# Check container details
docker inspect neural-navigator

# Test if app responds
curl http://localhost:5000
```

## Docker Image Details

- **Base Image**: `python:3.10-slim`
- **Size**: ~2.5GB (includes PyTorch)
- **Exposed Port**: 8080
- **Working Directory**: `/app/backend`
- **Entry Point**: `python app.py`

## Production Deployment

For production deployment to Docker hosting platforms:

### Push to Docker Hub
```bash
# Tag the image
docker tag neural-navigator your-username/neural-navigator:latest

# Login to Docker Hub
docker login

# Push
docker push your-username/neural-navigator:latest
```

### Deploy to Cloud Platforms
- **Fly.io**: Use `fly launch` (already configured with fly.toml)
- **Railway**: Connect GitHub repo, auto-detects Dockerfile
- **DigitalOcean App Platform**: Deploy from Docker Hub
- **AWS ECS**: Deploy container from ECR
- **Google Cloud Run**: Deploy from Container Registry

## Development Tips

### Live Reload (for development)
Mount your code and use a development server:

```bash
docker run -d \
  --name neural-navigator \
  -p 5000:8080 \
  -v "$(pwd)/backend:/app/backend" \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=true \
  neural-navigator
```

### Multi-stage Build (optimize size)
The current Dockerfile uses a slim image. For even smaller images, consider multi-stage builds.

### Custom Dockerfile
To modify the Docker setup, edit:
- `Dockerfile` - Main build configuration
- `docker-compose.yml` - Local development setup
- `.dockerignore` - Files to exclude from image

## Need Help?

- Docker Documentation: https://docs.docker.com/
- Flask in Docker: https://flask.palletsprojects.com/en/2.3.x/deploying/docker/
- PyTorch Docker: https://github.com/pytorch/pytorch#docker-image

## Summary of Files

- `Dockerfile` - Docker image definition
- `docker-compose.yml` - Multi-container orchestration (optional)
- `.dockerignore` - Files to exclude from Docker build
- `docker-run.sh` - Quick start script (Mac/Linux)
- `docker-run.bat` - Quick start script (Windows)
- `DOCKER.md` - This guide

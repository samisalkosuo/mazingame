#!/bin/bash
# Quick start script for Mazingame web deployment

set -e

echo "🎮 Mazingame Web Deployment"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and docker-compose are installed"
echo ""

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

if [ ! -d "logs" ]; then
    echo "📁 Creating logs directory..."
    mkdir -p logs
fi

echo ""
echo "🚀 Starting Mazingame web service..."
echo ""

# Build and start the service
docker-compose up -d --build

echo ""
echo "⏳ Waiting for service to be ready..."
sleep 5

# Check if service is running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Mazingame web service is running!"
    echo ""
    echo "🌐 Access the game at: http://localhost:5000"
    echo ""
    echo "📊 Useful commands:"
    echo "   View logs:        docker-compose logs -f"
    echo "   Stop service:     docker-compose down"
    echo "   Restart service:  docker-compose restart"
    echo "   View stats:       curl http://localhost:5000/api/stats"
    echo ""
else
    echo ""
    echo "❌ Failed to start service. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi

# Made with Bob

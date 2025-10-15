#!/bin/bash

echo "🚀 Starting HAZOP Management System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and set a secure JWT_SECRET!"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "✅ HAZOP System is starting!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is ready!"
else
    echo "⚠️  Backend is still starting... check logs with: docker-compose logs backend"
fi

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend is ready!"
else
    echo "⚠️  Frontend is still starting... check logs with: docker-compose logs frontend"
fi

echo ""
echo "🎉 Setup complete! Open http://localhost:5173 in your browser"

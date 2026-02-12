#!/bin/bash

# Startup script for Enterprise Integration Agents

echo "🚀 Enterprise Integration Agents with Azure AI Foundry"
echo "======================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your Azure credentials"
    echo ""
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your credentials"
    echo ""
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
required_vars=("AZURE_AI_PROJECT_ENDPOINT" "EVENTHUB_CONNECTION_STRING" "EVENTHUB_NAME")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "📝 Please configure these in your .env file"
    exit 1
fi

echo "✅ Environment configuration validated"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "📝 Please start Docker and try again"
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check Docker Compose version
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose --version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Error: Docker Compose is not installed"
    echo "📝 Please install Docker Compose and try again"
    exit 1
fi

echo "✅ Docker Compose found"
echo ""

# Parse command line arguments
COMMAND=${1:-up}

case $COMMAND in
    up)
        echo "🏗️  Building and starting all patterns..."
        echo ""
        $DOCKER_COMPOSE up --build -d
        echo ""
        echo "✅ All patterns started successfully!"
        echo ""
        echo "📡 API Endpoints:"
        echo "   - Pattern 1 (Message Queue):      http://localhost:8000"
        echo "   - Pattern 2 (Pipes & Filters):    http://localhost:8001"
        echo "   - Pattern 3 (Pub/Sub):            http://localhost:8002"
        echo "   - Pattern 4 (Command Messages):   http://localhost:8003"
        echo ""
        echo "📚 API Documentation:"
        echo "   - Pattern 1: http://localhost:8000/docs"
        echo "   - Pattern 2: http://localhost:8001/docs"
        echo "   - Pattern 3: http://localhost:8002/docs"
        echo "   - Pattern 4: http://localhost:8003/docs"
        echo ""
        echo "📊 View logs: ./start.sh logs"
        echo "🛑 Stop all:  ./start.sh down"
        ;;
    
    down)
        echo "🛑 Stopping all patterns..."
        $DOCKER_COMPOSE down
        echo ""
        echo "✅ All patterns stopped"
        ;;
    
    logs)
        echo "📊 Showing logs (Ctrl+C to exit)..."
        echo ""
        $DOCKER_COMPOSE logs -f
        ;;
    
    status)
        echo "📊 Pattern Status:"
        echo ""
        $DOCKER_COMPOSE ps
        ;;
    
    restart)
        echo "🔄 Restarting all patterns..."
        $DOCKER_COMPOSE restart
        echo ""
        echo "✅ All patterns restarted"
        ;;
    
    build)
        echo "🏗️  Building all patterns..."
        $DOCKER_COMPOSE build
        echo ""
        echo "✅ Build complete"
        ;;
    
    clean)
        echo "🧹 Cleaning up..."
        $DOCKER_COMPOSE down -v --remove-orphans
        docker system prune -f
        echo ""
        echo "✅ Cleanup complete"
        ;;
    
    *)
        echo "Usage: ./start.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up       - Build and start all patterns (default)"
        echo "  down     - Stop all patterns"
        echo "  logs     - Show logs from all patterns"
        echo "  status   - Show status of all patterns"
        echo "  restart  - Restart all patterns"
        echo "  build    - Build all patterns without starting"
        echo "  clean    - Stop and remove all containers, volumes, and images"
        echo ""
        exit 1
        ;;
esac

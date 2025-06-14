#!/bin/bash
# Robust build script with proper error handling

set -e  # Exit on error

echo "🚀 Starting build process with proper error handling..."

# Function to build with retry
build_service() {
    local service=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "📦 Building $service (attempt $attempt/$max_attempts)..."
        
        if timeout 600 docker-compose build --progress=plain $service; then
            echo "✅ $service built successfully!"
            return 0
        else
            echo "⚠️ Build failed for $service, attempt $attempt"
            
            # Clean up partial builds
            docker system prune -f
            
            if [ $attempt -lt $max_attempts ]; then
                echo "🔄 Retrying in 10 seconds..."
                sleep 10
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo "❌ Failed to build $service after $max_attempts attempts"
    return 1
}

# Ensure Docker daemon is responsive
echo "🔍 Checking Docker daemon..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker daemon not responding. Restarting..."
    sudo systemctl restart docker
    sleep 10
fi

# Clean up before building
echo "🧹 Cleaning up old images..."
docker system prune -f

# Build services
services=("portfolio" "proxy" "postgres" "analytics" "frontend" "backend")

for service in "${services[@]}"; do
    if ! build_service $service; then
        echo "❌ Build process failed. Please check the logs."
        exit 1
    fi
done

echo "✅ All services built successfully!"
echo "🔧 Starting services..."
docker-compose up -d

echo "🎉 Deployment complete!"
echo "📊 Container status:"
docker-compose ps
#!/bin/bash
# Complete replacement for 'docker compose up --build'
# Builds and runs containers sequentially to manage resource consumption
# Optimized for low-resource servers (1GB RAM, single CPU)
#
# USAGE:
#   chmod +x build-and-run.sh
#   ./build-and-run.sh
#
# This script replaces: docker compose up --build

set -e  # Exit on error

echo "🚀 Starting sequential build and run process..."

# Function to check system resources
check_resources() {
    echo "📊 System Resources:"
    echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
    echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
}

# Function to build with retry and resource management
build_service() {
    local service=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "📦 Building $service (attempt $attempt/$max_attempts)..."
        
        # Use single-threaded builds to reduce resource usage
        if timeout 900 docker-compose build --progress=plain --parallel 1 $service; then
            echo "✅ $service built successfully!"
            return 0
        else
            echo "⚠️ Build failed for $service, attempt $attempt"
            
            # Clean up partial builds and free memory
            docker system prune -f
            docker builder prune -f
            
            if [ $attempt -lt $max_attempts ]; then
                echo "🔄 Retrying in 30 seconds (letting system recover)..."
                sleep 30
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

# Build and start services sequentially to avoid resource spikes
services=("postgres" "portfolio" "proxy" "analytics" "frontend" "backend")

echo "🔧 Building and starting services one by one to manage resource consumption..."
check_resources

for service in "${services[@]}"; do
    echo "🏗️ Building $service..."
    if ! build_service $service; then
        echo "❌ Build process failed for $service. Please check the logs."
        exit 1
    fi
    
    echo "🚀 Starting $service..."
    docker-compose up -d $service
    
    # Wait for service to stabilize before proceeding
    echo "⏳ Waiting for $service to stabilize..."
    sleep 15
    
    # Check if service is running
    if docker-compose ps $service | grep -q "Up"; then
        echo "✅ $service is running successfully!"
    else
        echo "⚠️ Warning: $service may not be running properly"
        docker-compose logs --tail=10 $service
    fi
    
    # Brief pause to let system resources recover
    echo "💤 Letting system resources recover..."
    check_resources
    sleep 10
done

echo "🎉 Deployment complete!"
echo "📊 Container status:"
docker-compose ps
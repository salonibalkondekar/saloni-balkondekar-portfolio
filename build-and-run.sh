#!/bin/bash
# Simple sequential build script to prevent resource overload
# Builds and runs Docker containers one by one
# Optimized for low-resource servers (1GB RAM, single CPU)

set -e

echo "🚀 Starting sequential build process..."

# Define services in dependency order
services=("postgres" "portfolio" "proxy" "analytics" "frontend" "backend")

# Build and start each service sequentially
for service in "${services[@]}"; do
    echo "🏗️ Building and starting $service..."
    
    # Build the service
    docker compose build "$service"
    
    # Start the service without dependencies
    docker compose up -d --no-deps "$service"
    
    # Brief pause to let service stabilize
    sleep 5
    
    echo "✅ $service is running"
done

echo "🎉 All services deployed!"
echo "📊 Container status:"
docker compose ps
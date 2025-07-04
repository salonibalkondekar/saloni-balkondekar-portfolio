#!/bin/bash
# Improved sequential build script for low-resource servers
# Builds and runs Docker containers one by one with proper error handling
# Optimized for 1GB RAM, single CPU servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check system resources
check_resources() {
    log "📊 System Resources:"
    if command -v free &> /dev/null; then
        echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    fi
    if command -v uptime &> /dev/null; then
        echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
    fi
    if command -v df &> /dev/null; then
        echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2}')"
    fi
}

# Function to check if a service is healthy
check_service_health() {
    local service=$1
    local max_attempts=12
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose ps "$service" | grep -q "Up"; then
            success "$service is running!"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            warning "$service may not be running properly"
            docker compose logs --tail=5 "$service"
            return 1
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
}

# Function to build a service with error handling
build_service() {
    local service=$1
    local step_num=$2
    local total_steps=$3
    
    log "[$step_num/$total_steps] 🏗️ Building $service..."
    
    # Check if service needs building (skip postgres - it's a pre-built image)
    if [ "$service" = "postgres" ]; then
        log "Skipping build for $service (using pre-built image)"
        return 0
    fi
    
    # Build the service
    if timeout 600 docker compose build "$service"; then
        success "$service built successfully!"
        return 0
    else
        error "Failed to build $service"
        
        # Show build logs for debugging
        warning "Showing recent build logs:"
        docker compose logs --tail=10 "$service" 2>/dev/null || true
        
        return 1
    fi
}

# Function to start a service
start_service() {
    local service=$1
    local step_num=$2
    local total_steps=$3
    
    log "[$step_num/$total_steps] 🚀 Starting $service..."
    
    # Start the service without dependencies
    if docker compose up -d --no-deps "$service"; then
        # Brief pause to let service initialize
        sleep 3
        
        # Check if service started successfully
        if check_service_health "$service"; then
            return 0
        else
            warning "$service started but may not be healthy"
            return 1
        fi
    else
        error "Failed to start $service"
        docker compose logs --tail=10 "$service" 2>/dev/null || true
        return 1
    fi
}

# Main script starts here
log "🚀 Starting improved sequential build process..."

# Check initial resources
check_resources

# Define services in dependency order (proxy must be last)
# Note: Updated service names for clarity
services=(
    "postgres"              # Database (pre-built image)
    "analytics"             # Analytics service
    "text-to-cad-backend"   # Text-to-CAD API backend
    "text-to-cad-frontend"  # Text-to-CAD frontend
    "main-website"          # Portfolio website
    "news-gpt-app"          # News GPT application
    "deepresearch-app"      # DeepResearch application
    "proxy"                 # Nginx reverse proxy (must be last)
)

total_services=${#services[@]}
failed_services=()
successful_services=()

log "Building and starting $total_services services sequentially..."

# Process each service
for i in "${!services[@]}"; do
    service="${services[$i]}"
    step_num=$((i + 1))
    
    echo ""
    log "=== Processing $service ($step_num/$total_services) ==="
    
    # Build the service
    if build_service "$service" "$step_num" "$total_services"; then
        # Start the service
        if start_service "$service" "$step_num" "$total_services"; then
            successful_services+=("$service")
        else
            failed_services+=("$service")
            warning "Continuing with next service..."
        fi
    else
        failed_services+=("$service")
        warning "Skipping start for $service due to build failure"
    fi
    
    # Resource recovery pause (except for last service)
    if [ $step_num -lt $total_services ]; then
        log "💤 Letting system resources recover..."
        check_resources
        sleep 3
    fi
done

# Final status report
echo ""
log "🎉 Build process completed!"
echo ""

if [ ${#successful_services[@]} -gt 0 ]; then
    success "Successfully deployed services:"
    for service in "${successful_services[@]}"; do
        echo "  ✅ $service"
    done
fi

if [ ${#failed_services[@]} -gt 0 ]; then
    error "Failed services:"
    for service in "${failed_services[@]}"; do
        echo "  ❌ $service"
    done
    echo ""
    warning "You may need to check logs and fix issues for failed services"
fi

echo ""
log "📊 Final container status:"
docker compose ps

# Check if proxy is running (critical for website access)
if docker compose ps proxy | grep -q "Up"; then
    success "🌐 Website should be accessible at salonibalkondekar.codes"
else
    error "🌐 Proxy service is not running - website will not be accessible"
    warning "Check proxy service logs: docker compose logs proxy"
fi

# Exit with appropriate code
if [ ${#failed_services[@]} -eq 0 ]; then
    exit 0
else
    exit 1
fi
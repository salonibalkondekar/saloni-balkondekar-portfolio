#!/bin/bash
# Pre-deployment check script

echo "🔍 Running pre-deployment checks..."

# Check for merge conflicts
echo "📝 Checking for merge conflicts..."
if grep -r "<<<<<<< " . --include="*.py" --include="*.js" --include="*.html" 2>/dev/null; then
    echo "❌ Found merge conflicts! Please fix them first."
    exit 1
else
    echo "✅ No merge conflicts found"
fi

# Check Docker
echo "🐳 Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    exit 1
else
    echo "✅ Docker is running"
fi

# Check disk space
echo "💾 Checking disk space..."
available=$(df / | awk 'NR==2 {print $4}')
if [ $available -lt 5000000 ]; then  # Less than 5GB
    echo "⚠️ Low disk space: $(df -h / | awk 'NR==2 {print $4}') available"
    echo "Consider running: docker system prune -a"
else
    echo "✅ Sufficient disk space: $(df -h / | awk 'NR==2 {print $4}') available"
fi

# Check required files
echo "📁 Checking required files..."
required_files=(".env" "docker-compose.yml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        if [ "$file" == ".env" ]; then
            echo "💡 Copy .env.example to .env and configure it"
        fi
        exit 1
    fi
done
echo "✅ All required files present"

# Check environment variables
echo "🔐 Checking environment variables..."
if [ -f .env ]; then
    if ! grep -q "GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
        echo "⚠️ GEMINI_API_KEY not configured in .env"
    fi
    if ! grep -q "ADMIN_PASSWORD=" .env || grep -q "ADMIN_PASSWORD=change_me_in_production" .env; then
        echo "⚠️ ADMIN_PASSWORD not configured in .env"
    fi
fi

echo ""
echo "✅ Pre-deployment checks complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run: chmod +x build.sh"
echo "2. Run: ./build.sh"
echo "3. Or for manual build: docker-compose build && docker-compose up -d"
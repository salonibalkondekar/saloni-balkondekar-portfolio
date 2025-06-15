#!/usr/bin/env python3
"""
Quick Validation Script for Analytics Integration
Tests the core functionality to ensure everything works
"""

import subprocess
import sys
import os

def main():
    """Run validation tests"""
    print("🔍 Validating Analytics Integration")
    print("=" * 50)
    
    # Change to project root if we're in tests directory
    if os.path.basename(os.getcwd()) == "tests":
        os.chdir("..")
    
    print("1. Checking if services are running...")
    result = subprocess.run("docker-compose ps", shell=True, capture_output=True, text=True)
    if "analytics" in result.stdout and "backend" in result.stdout:
        print("✅ Services are running")
    else:
        print("❌ Services not running. Please run: docker-compose up -d")
        return False
    
    print("\n2. Testing analytics service directly...")
    # Try local development port first, then Docker exec
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200 and "healthy" in response.text:
            print("✅ Analytics service is healthy (via localhost:8001)")
            local_mode = True
        else:
            raise Exception("Not accessible via localhost")
    except:
        # Fall back to Docker exec
        result = subprocess.run(
            'docker exec $(docker ps -q -f name=analytics) curl -s http://localhost:8001/health',
            shell=True, capture_output=True, text=True
        )
        if '"status":"healthy"' in result.stdout:
            print("✅ Analytics service is healthy (via Docker exec)")
            local_mode = False
        else:
            print("❌ Analytics service not responding")
            return False
    
    print("\n3. Testing session creation...")
    result = subprocess.run(
        'docker exec $(docker ps -q -f name=analytics) curl -s -X POST http://localhost:8001/auth/create-session -d "email=validate@test.com&name=Validation User" -H "Content-Type: application/x-www-form-urlencoded"',
        shell=True, capture_output=True, text=True
    )
    if '"success":true' in result.stdout and '"model_count":0' in result.stdout:
        print("✅ Session creation works")
        print("✅ User tracking initialized (model_count: 0)")
    else:
        print("❌ Session creation failed")
        print(f"Response: {result.stdout}")
        return False
    
    print("\n4. Testing database schema...")
    result = subprocess.run(
        'docker exec $(docker ps -q -f name=postgres) psql -U analytics -d analytics_db -c "\\d cad_events" | grep model_id',
        shell=True, capture_output=True, text=True
    )
    if "model_id" in result.stdout:
        print("✅ Database schema includes model_id column")
    else:
        print("❌ Database schema missing model_id column")
        return False
    
    result = subprocess.run(
        'docker exec $(docker ps -q -f name=postgres) psql -U analytics -d analytics_db -c "\\d cad_events" | grep stl_file_path',
        shell=True, capture_output=True, text=True
    )
    if "stl_file_path" in result.stdout:
        print("✅ Database schema includes stl_file_path column")
    else:
        print("❌ Database schema missing stl_file_path column")
        return False
    
    print("\n5. Checking generated_models table...")
    result = subprocess.run(
        'docker exec $(docker ps -q -f name=postgres) psql -U analytics -d analytics_db -c "\\d generated_models"',
        shell=True, capture_output=True, text=True
    )
    if "generated_models" in result.stdout and "prompt" in result.stdout:
        print("✅ Generated models table exists with required columns")
    else:
        print("❌ Generated models table not properly configured")
        return False
    
    print("\n6. Testing new tracking endpoints...")
    result = subprocess.run(
        'docker exec $(docker ps -q -f name=analytics) curl -s -X POST http://localhost:8001/track/link-click -H "Content-Type: application/json" -d \'{"site":"portfolio","link_type":"test","metadata":{}}\'',
        shell=True, capture_output=True, text=True
    )
    if '"success":true' in result.stdout:
        print("✅ Portfolio link tracking endpoint works")
    else:
        print("❌ Portfolio link tracking endpoint failed")
        return False
    
    result = subprocess.run(
        'docker exec $(docker ps -q -f name=analytics) curl -s -X POST http://localhost:8001/track/scroll -H "Content-Type: application/json" -d \'{"site":"portfolio","scroll_percentage":50}\'',
        shell=True, capture_output=True, text=True
    )
    if '"success":true' in result.stdout:
        print("✅ Portfolio scroll tracking endpoint works")
    else:
        print("❌ Portfolio scroll tracking endpoint failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 VALIDATION SUCCESSFUL!")
    print("")
    print("✅ All services are running properly")
    print("✅ Analytics backend is operational")
    print("✅ User session management works")
    print("✅ Database schema is correct")
    print("✅ New tracking endpoints functional")
    print("✅ Data collection infrastructure is ready")
    print("")
    print("🚀 Your analytics integration is working!")
    print("💡 Ready for production use!")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        print("\n❌ Validation failed. Please check the issues above.")
        sys.exit(1)
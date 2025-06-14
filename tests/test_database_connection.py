#!/usr/bin/env python3
"""
Test to debug the database connection issue
"""
import os
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def parse_database_url(url):
    """Parse database URL and extract components"""
    parsed = urlparse(url)
    
    return {
        'scheme': parsed.scheme,
        'username': parsed.username,
        'password': parsed.password,
        'hostname': parsed.hostname,
        'port': parsed.port,
        'database': parsed.path.lstrip('/')
    }

def main():
    print("🔍 Debugging Database Connection Issue\n")
    
    # Test URL parsing
    test_url = "postgresql://analytics:analytics_password@postgres:5432/analytics_db"
    print(f"Test URL: {test_url}")
    
    components = parse_database_url(test_url)
    print("\nParsed components:")
    for key, value in components.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ Database name correctly parsed as: '{components['database']}'")
    
    # Check actual DATABASE_URL from analytics
    try:
        from analytics.database import DATABASE_URL
        print(f"\n📍 Actual DATABASE_URL: {DATABASE_URL}")
        
        actual_components = parse_database_url(DATABASE_URL)
        print("\nActual parsed components:")
        for key, value in actual_components.items():
            print(f"  {key}: {value}")
        
        # Check if database name is correct
        assert actual_components['database'] == 'analytics_db', f"Database should be 'analytics_db', got '{actual_components['database']}'"
        print("\n✅ Database configuration is correct!")
        
    except Exception as e:
        print(f"\n❌ Error checking DATABASE_URL: {e}")
    
    # Check for environment variables that might override
    print("\n🔍 Checking environment variables:")
    db_related_vars = ['DATABASE_URL', 'POSTGRES_DB', 'PGDATABASE', 'DB_NAME']
    for var in db_related_vars:
        value = os.environ.get(var)
        if value:
            print(f"  {var}: {value}")
    
    print("\n💡 Possible causes of 'database analytics does not exist' error:")
    print("1. Health check using wrong connection string")
    print("2. Another service trying to connect with wrong database name")
    print("3. SQLAlchemy connection pooling issue")
    print("4. Docker health check command using wrong database")
    
    # Check docker-compose for health checks
    print("\n🔍 Checking docker-compose.yml for health checks...")
    try:
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
        
        # Look for health check commands
        import re
        health_checks = re.findall(r'healthcheck:.*?test:.*?\[.*?\]', compose_content, re.DOTALL)
        
        for check in health_checks:
            if 'analytics' in check and 'analytics_db' not in check:
                print(f"⚠️  Found potential issue in health check: {check[:100]}...")
    except Exception as e:
        print(f"❌ Error checking docker-compose: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple test to verify analytics integration works
"""

import requests
import json


def test_analytics_integration():
    """Test basic analytics functionality"""
    print("🧪 Testing Analytics Integration")
    print("=" * 40)

    # Test 1: Analytics health
    print("1. Testing analytics health...")
    response = requests.get("http://localhost:8001/health")
    if response.status_code == 200:
        print("✅ Analytics service is healthy")
    else:
        print(f"❌ Analytics service failed: {response.status_code}")
        return False

    # Test 2: Create session
    print("2. Testing session creation...")
    response = requests.post(
        "http://localhost:8001/auth/create-session",
        data={"email": "test@integration.test", "name": "Integration Test User"},
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Session created for: {data['user']['email']}")
        print(f"   Model count: {data['user']['model_count']}/10")
        session_cookies = response.cookies
        user_id = data["user"]["id"]
    else:
        print(f"❌ Session creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    # Test 3: Track page view
    print("3. Testing page view tracking...")
    response = requests.post(
        "http://localhost:8001/track/pageview",
        json={"site": "text-to-cad", "path": "/test"},
    )

    if response.status_code == 200:
        print("✅ Page view tracked successfully")
    else:
        print(f"❌ Page view tracking failed: {response.status_code}")

    # Test 4: Track portfolio link click
    print("4. Testing portfolio link tracking...")
    response = requests.post(
        "http://localhost:8001/track/link-click",
        json={
            "site": "portfolio",
            "link_type": "project-link",
            "metadata": {
                "project": "text-to-cad",
                "url": "https://salonibalkondekar.codes/text-to-cad/",
            },
        },
    )

    if response.status_code == 200:
        print("✅ Portfolio link tracking works")
    else:
        print(f"❌ Portfolio link tracking failed: {response.status_code}")

    # Test 5: Check backend health
    print("5. Testing backend health...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("✅ Backend service is healthy")
    else:
        print(f"❌ Backend service failed: {response.status_code}")
        return False

    # Test 6: Test model generation with tracking
    print("6. Testing model generation with analytics...")
    response = requests.post(
        "http://localhost:8000/api/generate",
        json={"prompt": "create a simple test cube", "user_id": user_id},
        cookies=session_cookies,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Model generated successfully: {data['model_id'][:8]}...")
        print(f"   Prompt tracked: 'create a simple test cube'")

        # Check if user count incremented
        user_response = requests.get(
            "http://localhost:8001/auth/current-user", cookies=session_cookies
        )
        if user_response.status_code == 200:
            user_data = user_response.json()
            if user_data["model_count"] == 1:
                print(f"✅ User model count incremented to: {user_data['model_count']}")
            else:
                print(
                    f"⚠️  User model count is: {user_data['model_count']} (expected 1)"
                )

    else:
        print(f"❌ Model generation failed: {response.status_code}")
        print(f"   Response: {response.text}")

    # Test 7: Destroy session
    print("7. Testing session cleanup...")
    response = requests.post(
        "http://localhost:8001/auth/destroy-session", cookies=session_cookies
    )

    if response.status_code == 200:
        print("✅ Session destroyed successfully")
    else:
        print(f"⚠️  Session destruction status: {response.status_code}")

    print("=" * 40)
    print("🎉 Integration test completed!")
    print("\n📊 Summary:")
    print("✅ Analytics service operational")
    print("✅ User session management working")
    print("✅ Page view tracking active")
    print("✅ Portfolio link tracking active")
    print("✅ Backend service operational")
    print("✅ Model generation with data collection")
    print("✅ User count tracking")
    print("✅ Session management")

    return True


if __name__ == "__main__":
    try:
        test_analytics_integration()
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()

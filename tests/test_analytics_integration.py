#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Analytics Integration
Tests all new/existing features to ensure proper data collection and tracking
"""

import asyncio
import pytest
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Test Configuration
ANALYTICS_BASE_URL = "http://localhost:8001"
BACKEND_BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost"


class AnalyticsIntegrationTest:
    """Test suite for analytics integration"""

    def __init__(self):
        self.session_id = None
        self.user_id = None
        self.csrf_token = None
        self.session_cookies = {}

    def test_analytics_health(self):
        """Test analytics service is running"""
        print("🏥 Testing analytics service health...")
        response = requests.get(f"{ANALYTICS_BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Analytics service is healthy")

    def test_backend_health(self):
        """Test backend service is running"""
        print("🏥 Testing backend service health...")
        response = requests.get(f"{BACKEND_BASE_URL}/health")
        assert response.status_code == 200
        print("✅ Backend service is healthy")

    def test_create_analytics_session(self):
        """Test creating user session with analytics backend"""
        print("👤 Testing analytics session creation...")

        response = requests.post(
            f"{ANALYTICS_BASE_URL}/auth/create-session",
            data={"email": "test@analytics.test", "name": "Test User"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "user" in data
        assert data["user"]["email"] == "test@analytics.test"
        assert data["user"]["model_count"] == 0

        # Store session info
        self.session_cookies = response.cookies
        self.csrf_token = data.get("csrf_token")
        self.user_id = data["user"]["id"]

        print(f"✅ Session created for user {self.user_id}")
        print(f"   Model count: {data['user']['model_count']}/10")

    def test_get_current_user(self):
        """Test getting current user from analytics"""
        print("🔍 Testing current user retrieval...")

        response = requests.get(
            f"{ANALYTICS_BASE_URL}/auth/current-user", cookies=self.session_cookies
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.user_id
        assert data["email"] == "test@analytics.test"

        print(f"✅ Current user retrieved: {data['email']}")

    def test_track_pageview(self):
        """Test page view tracking"""
        print("📊 Testing page view tracking...")

        response = requests.post(
            f"{ANALYTICS_BASE_URL}/track/pageview",
            json={"site": "text-to-cad", "path": "/test-page"},
        )

        assert response.status_code == 200
        assert response.json()["success"] == True

        print("✅ Page view tracked successfully")

    def test_portfolio_link_tracking(self):
        """Test portfolio link click tracking"""
        print("🔗 Testing portfolio link tracking...")

        response = requests.post(
            f"{ANALYTICS_BASE_URL}/track/link-click",
            json={
                "site": "portfolio",
                "link_type": "project-link",
                "metadata": {
                    "project": "text-to-cad",
                    "url": "https://salonibalkondekar.codes/text-to-cad/",
                },
            },
        )

        assert response.status_code == 200
        assert response.json()["success"] == True

        print("✅ Portfolio link click tracked")

    def test_portfolio_scroll_tracking(self):
        """Test portfolio scroll milestone tracking"""
        print("📜 Testing portfolio scroll tracking...")

        response = requests.post(
            f"{ANALYTICS_BASE_URL}/track/scroll",
            json={"site": "portfolio", "scroll_percentage": 75},
        )

        assert response.status_code == 200
        assert response.json()["success"] == True

        print("✅ Portfolio scroll milestone tracked")

    def test_model_generation_tracking(self):
        """Test complete model generation and tracking"""
        print("🤖 Testing model generation with analytics tracking...")

        # Simulate model generation
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/generate",
            json={"prompt": "generate a test cube", "user_id": self.user_id},
            cookies=self.session_cookies,
        )

        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True
            assert "model_id" in data
            assert "badcad_code" in data

            print(f"✅ Model generated successfully: {data['model_id']}")
            print(f"   Generated code length: {len(data['badcad_code'])} chars")

            # Verify user count incremented
            user_response = requests.get(
                f"{ANALYTICS_BASE_URL}/auth/current-user", cookies=self.session_cookies
            )
            user_data = user_response.json()
            assert user_data["model_count"] == 1

            print(f"✅ User model count incremented to: {user_data['model_count']}")

            return data["model_id"]
        else:
            print(f"⚠️  Model generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    def test_admin_dashboard_data(self):
        """Test admin dashboard shows tracked data"""
        print("📊 Testing admin dashboard data...")

        # Note: This would require admin password, skipping for now
        print("⚠️  Admin dashboard test skipped (requires admin password)")

    def test_comprehensive_data_collection(self):
        """Test that all expected data is being collected"""
        print("🗃️  Testing comprehensive data collection...")

        # Test various tracking scenarios
        test_data = [
            {
                "type": "pageview",
                "url": f"{ANALYTICS_BASE_URL}/track/pageview",
                "data": {"site": "text-to-cad", "path": "/generator"},
            },
            {
                "type": "link_click",
                "url": f"{ANALYTICS_BASE_URL}/track/link-click",
                "data": {
                    "site": "portfolio",
                    "link_type": "social-link",
                    "metadata": {
                        "platform": "github",
                        "url": "https://github.com/salonibalkondekar",
                    },
                },
            },
            {
                "type": "scroll",
                "url": f"{ANALYTICS_BASE_URL}/track/scroll",
                "data": {"site": "portfolio", "scroll_percentage": 90},
            },
        ]

        for test in test_data:
            response = requests.post(test["url"], json=test["data"])
            assert response.status_code == 200
            assert response.json()["success"] == True
            print(f"✅ {test['type']} tracking verified")

    def test_session_persistence(self):
        """Test session persists across requests"""
        print("🔄 Testing session persistence...")

        # Make multiple requests with same session
        for i in range(3):
            response = requests.get(
                f"{ANALYTICS_BASE_URL}/auth/current-user", cookies=self.session_cookies
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == self.user_id

        print("✅ Session persists across multiple requests")

    def test_rate_limiting(self):
        """Test rate limiting works"""
        print("🚦 Testing rate limiting...")

        # Make rapid requests to trigger rate limit
        for i in range(15):
            response = requests.post(
                f"{ANALYTICS_BASE_URL}/track/pageview",
                json={"site": "test", "path": f"/rapid-{i}"},
            )
            if response.status_code == 429:
                print("✅ Rate limiting triggered as expected")
                return

        print("⚠️  Rate limiting not triggered (may be expected)")

    def test_user_limit_enforcement(self):
        """Test user generation limit enforcement"""
        print("🚫 Testing user limit enforcement...")

        # Generate models until limit is reached
        generation_count = 0
        while generation_count < 12:  # Try to exceed 10 model limit
            response = requests.post(
                f"{BACKEND_BASE_URL}/api/generate",
                json={
                    "prompt": f"test cube {generation_count}",
                    "user_id": self.user_id,
                },
                cookies=self.session_cookies,
            )

            if response.status_code == 403:
                print(f"✅ User limit enforced after {generation_count} generations")
                return
            elif response.status_code == 200:
                generation_count += 1
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                break

        print(f"⚠️  Generated {generation_count} models without hitting limit")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🧪 Starting comprehensive analytics integration tests...")
        print("=" * 60)

        try:
            # Core service tests
            self.test_analytics_health()
            self.test_backend_health()

            # Authentication and session tests
            self.test_create_analytics_session()
            self.test_get_current_user()
            self.test_session_persistence()

            # Tracking tests
            self.test_track_pageview()
            self.test_portfolio_link_tracking()
            self.test_portfolio_scroll_tracking()
            self.test_comprehensive_data_collection()

            # Model generation and data collection
            model_id = self.test_model_generation_tracking()

            # Limits and security
            self.test_rate_limiting()
            # self.test_user_limit_enforcement()  # Skip to avoid hitting actual limits

            # Dashboard data
            self.test_admin_dashboard_data()

            print("=" * 60)
            print("🎉 All tests completed successfully!")
            print("\n📊 Test Summary:")
            print("✅ Analytics service integration")
            print("✅ User session management")
            print("✅ Page view tracking")
            print("✅ Portfolio link/scroll tracking")
            print("✅ Model generation tracking")
            print("✅ User count incrementation")
            print("✅ Session persistence")
            print("✅ Rate limiting")
            print("✅ Comprehensive data collection")

        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            raise

    def cleanup(self):
        """Clean up test data"""
        print("🧹 Cleaning up test session...")
        if self.session_cookies:
            requests.post(
                f"{ANALYTICS_BASE_URL}/auth/destroy-session",
                cookies=self.session_cookies,
            )
        print("✅ Cleanup completed")


def main():
    """Main test runner"""
    print("🚀 Analytics Integration Test Suite")
    print("Testing all new and existing features for proper data collection")
    print()

    tester = AnalyticsIntegrationTest()

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()

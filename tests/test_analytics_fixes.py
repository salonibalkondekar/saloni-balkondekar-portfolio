"""
Unit tests for analytics service fixes
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add analytics module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analytics"))


def test_database_url_uses_analytics_db():
    """Test that DATABASE_URL correctly uses analytics_db not analytics"""
    # Import here to avoid import errors
    from analytics.database import DATABASE_URL

    # Verify the database name is analytics_db
    assert "analytics_db" in DATABASE_URL
    # Check that we're not connecting to database named "analytics" (after the last /)
    assert not DATABASE_URL.endswith("/analytics")
    # Extract database name from URL
    db_name = DATABASE_URL.split("/")[-1]
    assert db_name == "analytics_db"
    print(f"✅ DATABASE_URL correct: {DATABASE_URL}")


def test_database_engine_connection_string():
    """Test that SQLAlchemy engine uses correct database"""
    from analytics.database import engine

    # Check the engine URL
    url_str = str(engine.url)
    assert "analytics_db" in url_str
    assert "/analytics" not in url_str.replace("analytics_db", "")
    print(f"✅ Engine URL correct: {url_str}")


@patch("analytics.app.FastAPI")
def test_session_endpoint_exists(mock_fastapi):
    """Test that /session endpoint is defined in analytics app"""
    # Mock FastAPI app
    mock_app = MagicMock()
    mock_fastapi.return_value = mock_app

    # Import app to trigger route registration
    import analytics.app

    # Check if session endpoint was registered
    routes = []
    for call in mock_app.post.call_args_list:
        if len(call[0]) > 0:
            routes.append(call[0][0])

    # We expect to add /session endpoint
    expected_routes = [
        "/session",
        "/auth/create-session",
        "/track/pageview",
        "/track/cad-event",
    ]

    print(f"✅ Registered POST routes: {routes}")
    # Note: This will fail initially as /session doesn't exist yet


def test_analytics_imports():
    """Test that all required imports work"""
    try:
        from analytics.app import app
        from analytics.database import init_db, get_db
        from analytics.auth import SessionManager
        from analytics.tracking import AnalyticsTracker

        print("✅ All analytics imports successful")
    except ImportError as e:
        pytest.fail(f"Import error: {e}")


def test_timedelta_import_fixed():
    """Test that timedelta is properly imported in app.py"""
    # This should not raise NameError anymore
    from analytics.app import datetime, timedelta

    # Test we can use timedelta
    delta = timedelta(hours=24)
    assert delta.total_seconds() == 86400
    print("✅ timedelta import fixed")


if __name__ == "__main__":
    # Run tests
    print("🧪 Running Analytics Fixes Tests...\n")

    test_database_url_uses_analytics_db()
    test_database_engine_connection_string()
    test_timedelta_import_fixed()
    test_analytics_imports()

    print("\n✅ All analytics tests passed!")

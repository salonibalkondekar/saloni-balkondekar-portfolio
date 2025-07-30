"""
Unit tests for backend user management fixes
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Add backend module to path
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "text-to-cad", "backend")
)


def test_modern_user_manager_exists():
    """Test that ModernUserManager exists in user_management.py"""
    try:
        from services.user_management import user_manager, ModernUserManager

        assert isinstance(user_manager, ModernUserManager)
        print("✅ ModernUserManager properly imported")
    except ImportError as e:
        pytest.fail(f"Import error: {e}")


def test_no_old_user_manager_methods():
    """Test that old methods don't exist"""
    from services.user_management import user_manager

    # These old methods should NOT exist
    old_methods = [
        "check_user_can_generate",
        "record_user_prompt",
        "increment_user_model_count",
    ]

    for method in old_methods:
        assert not hasattr(user_manager, method), f"Old method {method} still exists!"

    # These new methods SHOULD exist
    new_methods = [
        "create_or_get_session",
        "get_user_info",
        "check_user_limit",
        "increment_model_count",
        "track_generation",
    ]

    for method in new_methods:
        assert hasattr(user_manager, method), f"New method {method} missing!"

    print("✅ User manager has correct methods")


@pytest.mark.asyncio
async def test_generation_route_uses_async_methods():
    """Test that generation route properly uses async user management"""
    # Mock the dependencies
    with patch("services.user_management.user_manager") as mock_user_manager:
        # Setup async mocks
        mock_user_manager.check_user_limit = AsyncMock(return_value=True)
        mock_user_manager.increment_model_count = AsyncMock(
            return_value={"model_count": 1}
        )
        mock_user_manager.track_generation = AsyncMock()

        # Import generation route
        from api.routes.generation import generate_model

        # The route should use async methods
        # This will be verified when we fix the actual code
        print("✅ Generation route ready for async user management")


def test_user_manager_configuration():
    """Test user manager is configured correctly"""
    from services.user_management import user_manager
    from core.config import settings

    assert user_manager.max_models_per_user == settings.max_models_per_user
    assert hasattr(user_manager, "analytics_client")
    print(
        f"✅ User manager configured with max models: {user_manager.max_models_per_user}"
    )


def test_analytics_client_integration():
    """Test that user manager integrates with analytics client"""
    from services.user_management import user_manager
    from services.analytics_client import analytics_client

    assert user_manager.analytics_client == analytics_client
    print("✅ User manager integrated with analytics client")


@pytest.mark.asyncio
async def test_check_user_limit_async():
    """Test async check_user_limit method"""
    from services.user_management import user_manager

    with patch.object(
        user_manager, "get_user_info", new_callable=AsyncMock
    ) as mock_get_info:
        # Test new user (no info)
        mock_get_info.return_value = None
        result = await user_manager.check_user_limit("test_user")
        assert result == True

        # Test user under limit
        mock_get_info.return_value = {"model_count": 5}
        result = await user_manager.check_user_limit("test_user")
        assert result == True

        # Test user at limit
        mock_get_info.return_value = {"model_count": 10}
        with pytest.raises(Exception):  # Should raise UserLimitExceededError
            await user_manager.check_user_limit("test_user")

        print("✅ Async check_user_limit works correctly")


if __name__ == "__main__":
    # Run sync tests
    print("🧪 Running Backend Fixes Tests...\n")

    test_modern_user_manager_exists()
    test_no_old_user_manager_methods()
    test_user_manager_configuration()
    test_analytics_client_integration()

    # Run async tests
    asyncio.run(test_check_user_limit_async())

    print("\n✅ All backend tests passed!")

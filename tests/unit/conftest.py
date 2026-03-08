"""Unit test fixtures."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture(autouse=True)
def mock_container():
    """Mock container for unit tests."""
    # Create mock container
    container = MagicMock()
    
    # Mock use cases
    use_cases = MagicMock()
    use_cases.fetch_instagram_profile = AsyncMock()
    use_cases.fetch_instagram_profile.execute = AsyncMock()
    use_cases.fetch_instagram_stories = AsyncMock()
    use_cases.fetch_instagram_stories.execute = AsyncMock()
    use_cases.fetch_instagram_posts = AsyncMock()
    use_cases.fetch_instagram_posts.execute = AsyncMock()
    use_cases.fetch_instagram_reels = AsyncMock()
    use_cases.fetch_instagram_reels.execute = AsyncMock()
    use_cases.fetch_instagram_highlights = AsyncMock()
    use_cases.fetch_instagram_highlights.execute = AsyncMock()
    use_cases.fetch_instagram_followers = AsyncMock()
    use_cases.fetch_instagram_followers.execute = AsyncMock()
    use_cases.fetch_instagram_following = AsyncMock()
    use_cases.fetch_instagram_following.execute = AsyncMock()
    use_cases.get_user_trackings = AsyncMock()
    use_cases.get_user_trackings.execute = AsyncMock(return_value=[])
    use_cases.start_tracking = AsyncMock()
    use_cases.start_tracking.execute = AsyncMock()
    use_cases.stop_tracking = AsyncMock()
    use_cases.stop_tracking.execute = AsyncMock()
    use_cases.create_payment = AsyncMock()
    use_cases.create_payment.execute = AsyncMock()
    use_cases.complete_payment = AsyncMock()
    use_cases.complete_payment.execute = AsyncMock()
    use_cases.create_subscription = AsyncMock()
    use_cases.create_subscription.execute = AsyncMock()
    use_cases.check_subscription_status = AsyncMock()
    use_cases.check_subscription_status.execute = AsyncMock()
    
    container.get_use_cases.return_value = use_cases
    
    # Patch all get_container calls
    with patch("src.presentation.telegram.handlers.instagram_handlers.get_container", return_value=container):
        with patch("src.presentation.telegram.handlers.payment_handlers.get_container", return_value=container):
            with patch("src.presentation.telegram.handlers.tracking_handlers.get_container", return_value=container):
                yield container

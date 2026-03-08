"""Integration tests for tracking flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.presentation.telegram.handlers.tracking_handlers import (
    tracking_start_callback,
    handle_tracking_type_selection,
    handle_tracking_interval_set,
    tracking_stop_callback,
)


@pytest.mark.asyncio
class TestTrackingStartFlow:
    """Test tracking start flow."""
    
    async def test_tracking_start_shows_menu(self):
        """Test that tracking start shows configuration menu."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "ig_track_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        
        await tracking_start_callback(callback)
        
        # Verify callback was answered
        callback.answer.assert_called_once()
        
        # Verify menu was shown
        callback.message.edit_text.assert_called_once()
        call_args = callback.message.edit_text.call_args
        assert "Отслеживание" in call_args[0][0]
        assert "Stories" in call_args[0][0]
        assert "Posts" in call_args[0][0]
    
    async def test_tracking_type_selection(self):
        """Test tracking type selection."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "track_type_stories_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        
        await handle_tracking_type_selection(callback)
        
        # Verify interval menu was shown
        callback.message.edit_text.assert_called_once()
        call_args = callback.message.edit_text.call_args
        assert "интервал" in call_args[0][0].lower()
        assert "Stories" in call_args[0][0]


@pytest.mark.asyncio
class TestTrackingIntervalFlow:
    """Test tracking interval selection flow."""
    
    async def test_interval_set_success(self):
        """Test successful interval setting."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "track_interval_stories_1h_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock subscription DTO
        from src.application.subscription.dtos import SubscriptionDTO
        sub_status = SubscriptionDTO(
            id=1,
            user_id=123,
            subscription_type="PREMIUM",
            status="ACTIVE",
            start_date=datetime.now().isoformat(),
            end_date=datetime.now().isoformat(),
            days_remaining=30,
            is_active=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        
        # Mock Use Cases
        with patch("src.presentation.telegram.handlers.tracking_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_check_sub = AsyncMock()
            mock_check_sub.execute = AsyncMock(return_value=sub_status)
            mock_use_cases.check_subscription_status = mock_check_sub
            
            mock_start_tracking = AsyncMock()
            mock_start_tracking.execute = AsyncMock()
            mock_use_cases.start_tracking = mock_start_tracking
            
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await handle_tracking_interval_set(callback)
            
            # Verify tracking was started
            mock_start_tracking.execute.assert_called_once()
            
            # Verify success message
            callback.message.answer.assert_called_once()
            call_args = callback.message.answer.call_args
            assert "активировано" in call_args[0][0].lower()
    
    async def test_interval_set_no_subscription(self):
        """Test interval setting without subscription."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "track_interval_stories_1h_123_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock subscription DTO (inactive)
        from src.application.subscription.dtos import SubscriptionDTO
        sub_status = SubscriptionDTO(
            id=1,
            user_id=123,
            subscription_type="PREMIUM",
            status="EXPIRED",
            start_date=datetime.now().isoformat(),
            end_date=datetime.now().isoformat(),
            days_remaining=0,
            is_active=False,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        
        # Mock Use Cases
        with patch("src.presentation.telegram.handlers.tracking_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_check_sub = AsyncMock()
            mock_check_sub.execute = AsyncMock(return_value=sub_status)
            mock_use_cases.check_subscription_status = mock_check_sub
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await handle_tracking_interval_set(callback)
            
            # Verify error message about subscription
            callback.message.answer.assert_called_once()
            call_args = callback.message.answer.call_args
            assert "подписка" in call_args[0][0].lower()


@pytest.mark.asyncio
class TestTrackingStopFlow:
    """Test tracking stop flow."""
    
    async def test_tracking_stop_success(self):
        """Test successful tracking stop."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "unsubscribe_tracking_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock tracking DTO
        from src.application.content_tracking.dtos import TrackingDTO
        tracking = TrackingDTO(
            tracking_id="track_1",
            user_id="123",
            instagram_user_id="456",
            instagram_username="testuser",
            content_type="stories",
            status="active",
            check_interval_minutes=60,
            notification_enabled=True,
            last_check_at=None,
            last_content_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        # Add id attribute for compatibility
        tracking.id = "track_1"
        
        # Mock Use Cases
        with patch("src.presentation.telegram.handlers.tracking_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_get_trackings = AsyncMock()
            mock_get_trackings.execute = AsyncMock(return_value=[tracking])
            mock_use_cases.get_user_trackings = mock_get_trackings
            
            mock_stop_tracking = AsyncMock()
            mock_stop_tracking.execute = AsyncMock()
            mock_use_cases.stop_tracking = mock_stop_tracking
            
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await tracking_stop_callback(callback)
            
            # Verify tracking was stopped
            mock_stop_tracking.execute.assert_called_once_with("track_1")
            
            # Verify success message
            callback.message.edit_text.assert_called_once()
            call_args = callback.message.edit_text.call_args
            assert "отписались" in call_args[0][0].lower()
    
    async def test_tracking_stop_not_found(self):
        """Test tracking stop when tracking not found."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "unsubscribe_tracking_testuser"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock Use Cases (no trackings)
        with patch("src.presentation.telegram.handlers.tracking_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_use_cases.get_user_trackings = AsyncMock(return_value=[])
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await tracking_stop_callback(callback)
            
            # Verify error message
            callback.message.edit_text.assert_called_once()
            call_args = callback.message.edit_text.call_args
            assert "не найдено" in call_args[0][0].lower()

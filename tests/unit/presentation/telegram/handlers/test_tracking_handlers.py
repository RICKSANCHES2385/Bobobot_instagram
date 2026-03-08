"""Tests for tracking handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import CallbackQuery, User

from src.presentation.telegram.handlers.tracking_handlers import (
    tracking_start_callback,
    handle_tracking_type_selection,
    handle_tracking_interval_set,
    tracking_stop_callback,
    my_trackings_callback,
    get_tracking_menu_keyboard,
    get_tracking_interval_keyboard,
)


@pytest.mark.asyncio
class TestTrackingHandlers:
    """Tests for tracking handlers."""

    @pytest.fixture
    def mock_callback(self):
        """Create mock callback query."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.message.delete = AsyncMock()
        callback.answer = AsyncMock()
        return callback

    async def test_tracking_start_callback(self, mock_callback):
        """Test tracking_start_callback."""
        mock_callback.data = "ig_track_123_cristiano"
        
        await tracking_start_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()

    async def test_handle_tracking_type_selection(self, mock_callback):
        """Test handle_tracking_type_selection."""
        mock_callback.data = "track_type_stories_123_cristiano"
        
        await handle_tracking_type_selection(mock_callback)
        
        mock_callback.answer.assert_called_once()

    async def test_handle_tracking_interval_set(self, mock_callback, mock_container):
        """Test handle_tracking_interval_set."""
        mock_callback.data = "track_interval_stories_1h_123_cristiano"
        
        # Setup mocks
        mock_use_cases = mock_container.get_use_cases.return_value
        mock_check_sub = AsyncMock()
        mock_check_sub.execute = AsyncMock(return_value=MagicMock(is_active=True))
        mock_use_cases.check_subscription_status = mock_check_sub
        
        mock_start_tracking = AsyncMock()
        mock_start_tracking.execute = AsyncMock()
        mock_use_cases.start_tracking = mock_start_tracking
        
        await handle_tracking_interval_set(mock_callback)
        
        mock_callback.answer.assert_called_once()

    async def test_tracking_stop_callback(self, mock_callback, mock_container):
        """Test tracking_stop_callback."""
        mock_callback.data = "unsubscribe_tracking_cristiano"
        
        # Setup mocks
        mock_use_cases = mock_container.get_use_cases.return_value
        mock_get_trackings = AsyncMock()
        mock_get_trackings.execute = AsyncMock(return_value=[])
        mock_use_cases.get_user_trackings = mock_get_trackings
        
        await tracking_stop_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()

    async def test_my_trackings_callback(self, mock_callback):
        """Test my_trackings_callback."""
        await my_trackings_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()

    def test_get_tracking_menu_keyboard(self):
        """Test get_tracking_menu_keyboard."""
        keyboard = get_tracking_menu_keyboard("123", "cristiano")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 5

    def test_get_tracking_interval_keyboard(self):
        """Test get_tracking_interval_keyboard."""
        keyboard = get_tracking_interval_keyboard("stories", "123", "cristiano")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 5

"""Tests for Instagram handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram.types import CallbackQuery, Message, User

from src.presentation.telegram.handlers.instagram_handlers import (
    parse_instagram_username,
    handle_stories,
    handle_posts,
    handle_reels,
    handle_highlights,
    handle_followers,
    handle_following,
    handle_profile_callback,
    handle_back_to_profile,
)


class TestParseInstagramUsername:
    """Tests for parse_instagram_username function."""

    def test_parse_simple_username(self):
        """Test parsing simple username."""
        assert parse_instagram_username("cristiano") == "cristiano"

    def test_parse_username_with_at(self):
        """Test parsing username with @ prefix."""
        assert parse_instagram_username("@cristiano") == "cristiano"

    def test_parse_instagram_url(self):
        """Test parsing Instagram URL."""
        assert parse_instagram_username("https://instagram.com/cristiano") == "cristiano"
        assert parse_instagram_username("https://instagram.com/cristiano/") == "cristiano"
        assert parse_instagram_username("https://www.instagram.com/cristiano") == "cristiano"

    def test_parse_instagr_am_url(self):
        """Test parsing instagr.am URL."""
        assert parse_instagram_username("https://instagr.am/cristiano") == "cristiano"

    def test_parse_invalid_username(self):
        """Test parsing invalid username."""
        assert parse_instagram_username("invalid username!") is None
        assert parse_instagram_username("") is None


@pytest.mark.asyncio
class TestInstagramHandlers:
    """Tests for Instagram handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create mock message."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()
        message.delete = AsyncMock()
        return message

    @pytest.fixture
    def mock_callback(self):
        """Create mock callback query."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.message = AsyncMock(spec=Message)
        callback.message.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.message.delete = AsyncMock()
        callback.answer = AsyncMock()
        return callback

    async def test_handle_stories(self, mock_callback):
        """Test handle_stories callback."""
        mock_callback.data = "ig_stories_123_cristiano"
        
        await handle_stories(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        assert "Stories" in mock_callback.message.answer.call_args[0][0]

    async def test_handle_posts(self, mock_callback):
        """Test handle_posts callback."""
        mock_callback.data = "ig_posts_123_cristiano"
        
        await handle_posts(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        assert "Posts" in mock_callback.message.answer.call_args[0][0]

    async def test_handle_reels(self, mock_callback):
        """Test handle_reels callback."""
        mock_callback.data = "ig_reels_123_cristiano"
        
        await handle_reels(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        assert "Reels" in mock_callback.message.answer.call_args[0][0]

    async def test_handle_highlights(self, mock_callback):
        """Test handle_highlights callback."""
        mock_callback.data = "ig_highlights_123_cristiano"
        
        await handle_highlights(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        assert "Highlights" in mock_callback.message.answer.call_args[0][0]

    async def test_handle_followers(self, mock_callback):
        """Test handle_followers callback."""
        mock_callback.data = "ig_followers_123_cristiano"
        
        await handle_followers(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        assert "Подписчики" in mock_callback.message.answer.call_args[0][0]

    async def test_handle_following(self, mock_callback):
        """Test handle_following callback."""
        mock_callback.data = "ig_following_123_cristiano"
        
        await handle_following(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.answer.assert_called_once()
        assert "Подписки" in mock_callback.message.answer.call_args[0][0]

    async def test_handle_profile_callback(self, mock_callback):
        """Test handle_profile_callback."""
        mock_callback.data = "ig_profile_123_cristiano"
        
        with patch("src.presentation.telegram.handlers.instagram_handlers.send_user_profile") as mock_send:
            mock_send.return_value = AsyncMock()
            await handle_profile_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.delete.assert_called_once()

    async def test_handle_back_to_profile(self, mock_callback):
        """Test handle_back_to_profile."""
        mock_callback.data = "ig_back_123_cristiano"
        
        with patch("src.presentation.telegram.handlers.instagram_handlers.send_user_profile") as mock_send:
            mock_send.return_value = AsyncMock()
            await handle_back_to_profile(mock_callback)
        
        mock_callback.answer.assert_called_once()
        mock_callback.message.delete.assert_called_once()

    async def test_handle_invalid_callback_data(self, mock_callback):
        """Test handling invalid callback data."""
        mock_callback.data = "ig_stories_invalid"
        
        await handle_stories(mock_callback)
        
        mock_callback.answer.assert_called_with("❌ Ошибка данных", show_alert=True)

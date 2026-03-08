"""Tests for subscription check middleware."""

import pytest
from unittest.mock import AsyncMock

from aiogram.types import Message, CallbackQuery, User

from src.presentation.telegram.middleware.subscription_check import (
    SubscriptionCheckMiddleware,
    FeatureAccessMiddleware,
)


@pytest.mark.asyncio
class TestSubscriptionCheckMiddleware:
    """Tests for SubscriptionCheckMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return SubscriptionCheckMiddleware()

    @pytest.fixture
    def mock_message(self):
        """Create mock message."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "/instagram cristiano"
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    def mock_callback(self):
        """Create mock callback."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "ig_stories_123_cristiano"
        callback.answer = AsyncMock()
        return callback

    @pytest.fixture
    def mock_handler(self):
        """Create mock handler."""
        return AsyncMock()

    async def test_allows_exempt_commands(self, middleware, mock_handler):
        """Test that exempt commands are allowed."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "/start"
        message.answer = AsyncMock()
        
        await middleware(mock_handler, message, {})
        
        mock_handler.assert_called_once()

    async def test_allows_help_command(self, middleware, mock_handler):
        """Test that /help command is allowed."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "/help"
        message.answer = AsyncMock()
        
        await middleware(mock_handler, message, {})
        
        mock_handler.assert_called_once()

    async def test_allows_tariffs_command(self, middleware, mock_handler):
        """Test that /tariffs command is allowed."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "/tariffs"
        message.answer = AsyncMock()
        
        await middleware(mock_handler, message, {})
        
        mock_handler.assert_called_once()

    async def test_allows_payment_callbacks(self, middleware, mock_handler):
        """Test that payment callbacks are allowed."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "payment_stars"
        callback.answer = AsyncMock()
        
        await middleware(mock_handler, callback, {})
        
        mock_handler.assert_called_once()

    async def test_allows_buy_callbacks(self, middleware, mock_handler):
        """Test that buy callbacks are allowed."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "buy_1m"
        callback.answer = AsyncMock()
        
        await middleware(mock_handler, callback, {})
        
        mock_handler.assert_called_once()

    async def test_passes_through_other_requests(self, middleware, mock_message, mock_handler):
        """Test that other requests pass through (for now)."""
        await middleware(mock_handler, mock_message, {})
        
        # Currently passes through, will check subscription in production
        mock_handler.assert_called_once()


@pytest.mark.asyncio
class TestFeatureAccessMiddleware:
    """Tests for FeatureAccessMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return FeatureAccessMiddleware()

    @pytest.fixture
    def mock_callback(self):
        """Create mock callback."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "ig_stories_123_cristiano"
        callback.answer = AsyncMock()
        return callback

    @pytest.fixture
    def mock_handler(self):
        """Create mock handler."""
        return AsyncMock()

    async def test_allows_non_premium_features(self, middleware, mock_callback, mock_handler):
        """Test that non-premium features are allowed."""
        await middleware(mock_handler, mock_callback, {})
        
        mock_handler.assert_called_once()

    async def test_checks_premium_features(self, middleware, mock_handler):
        """Test that premium features are checked."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "track_audience_123_cristiano"
        callback.answer = AsyncMock()
        
        await middleware(mock_handler, callback, {})
        
        # Currently passes through, will check premium in production
        mock_handler.assert_called_once()

    async def test_checks_download_features(self, middleware, mock_handler):
        """Test that download features are checked."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.data = "ig_followers_dl_123_cristiano"
        callback.answer = AsyncMock()
        
        await middleware(mock_handler, callback, {})
        
        # Currently passes through, will check premium in production
        mock_handler.assert_called_once()

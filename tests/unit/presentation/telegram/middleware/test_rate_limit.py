"""Tests for rate limit middleware."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock

from aiogram.types import Message, CallbackQuery, User

from src.presentation.telegram.middleware.rate_limit import (
    RateLimitMiddleware,
    CommandRateLimitMiddleware,
)


@pytest.mark.asyncio
class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return RateLimitMiddleware(rate_limit=5, time_window=60)

    @pytest.fixture
    def mock_message(self):
        """Create mock message."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    def mock_callback(self):
        """Create mock callback."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.answer = AsyncMock()
        return callback

    @pytest.fixture
    def mock_handler(self):
        """Create mock handler."""
        return AsyncMock()

    async def test_allows_requests_under_limit(self, middleware, mock_message, mock_handler):
        """Test that requests under limit are allowed."""
        for _ in range(5):
            await middleware(mock_handler, mock_message, {})
        
        assert mock_handler.call_count == 5

    async def test_blocks_requests_over_limit(self, middleware, mock_message, mock_handler):
        """Test that requests over limit are blocked."""
        # Make 5 requests (at limit)
        for _ in range(5):
            await middleware(mock_handler, mock_message, {})
        
        # 6th request should be blocked
        await middleware(mock_handler, mock_message, {})
        
        assert mock_handler.call_count == 5
        mock_message.answer.assert_called_once()

    async def test_blocks_callback_over_limit(self, middleware, mock_callback, mock_handler):
        """Test that callbacks over limit are blocked."""
        # Make 5 requests (at limit)
        for _ in range(5):
            await middleware(mock_handler, mock_callback, {})
        
        # 6th request should be blocked
        await middleware(mock_handler, mock_callback, {})
        
        assert mock_handler.call_count == 5
        mock_callback.answer.assert_called()

    async def test_different_users_independent_limits(self, middleware, mock_handler):
        """Test that different users have independent limits."""
        user1_message = AsyncMock(spec=Message)
        user1_message.from_user = User(id=1, is_bot=False, first_name="User1")
        user1_message.answer = AsyncMock()
        
        user2_message = AsyncMock(spec=Message)
        user2_message.from_user = User(id=2, is_bot=False, first_name="User2")
        user2_message.answer = AsyncMock()
        
        # User 1 makes 5 requests
        for _ in range(5):
            await middleware(mock_handler, user1_message, {})
        
        # User 2 should still be able to make requests
        await middleware(mock_handler, user2_message, {})
        
        assert mock_handler.call_count == 6


@pytest.mark.asyncio
class TestCommandRateLimitMiddleware:
    """Tests for CommandRateLimitMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        return CommandRateLimitMiddleware(limits={"/test": (3, 60)})

    @pytest.fixture
    def mock_message(self):
        """Create mock message."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "/test"
        message.answer = AsyncMock()
        return message

    @pytest.fixture
    def mock_handler(self):
        """Create mock handler."""
        return AsyncMock()

    async def test_allows_commands_under_limit(self, middleware, mock_message, mock_handler):
        """Test that commands under limit are allowed."""
        for _ in range(3):
            await middleware(mock_handler, mock_message, {})
        
        assert mock_handler.call_count == 3

    async def test_blocks_commands_over_limit(self, middleware, mock_message, mock_handler):
        """Test that commands over limit are blocked."""
        # Make 3 requests (at limit)
        for _ in range(3):
            await middleware(mock_handler, mock_message, {})
        
        # 4th request should be blocked
        await middleware(mock_handler, mock_message, {})
        
        assert mock_handler.call_count == 3
        mock_message.answer.assert_called_once()

    async def test_unlimited_command_not_blocked(self, middleware, mock_handler):
        """Test that unlimited commands are not blocked."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "/unlimited"
        message.answer = AsyncMock()
        
        # Make many requests
        for _ in range(10):
            await middleware(mock_handler, message, {})
        
        assert mock_handler.call_count == 10

    async def test_non_command_message_not_blocked(self, middleware, mock_handler):
        """Test that non-command messages are not blocked."""
        message = AsyncMock(spec=Message)
        message.from_user = User(id=123, is_bot=False, first_name="Test")
        message.text = "regular message"
        message.answer = AsyncMock()
        
        # Make many requests
        for _ in range(10):
            await middleware(mock_handler, message, {})
        
        assert mock_handler.call_count == 10

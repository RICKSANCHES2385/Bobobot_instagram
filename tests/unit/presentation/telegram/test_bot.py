"""Tests for Telegram bot."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.config import Settings
from src.presentation.telegram.bot import TelegramBot


@pytest.mark.asyncio
class TestTelegramBot:
    """Test Telegram bot initialization."""

    @patch("src.presentation.telegram.bot.Bot")
    def test_bot_initialization(self, mock_bot: MagicMock) -> None:
        """Test bot can be initialized."""
        # Arrange
        settings = Settings(
            telegram_bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            environment="test",
            database_url="sqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
            hikerapi_key="test_key",
        )

        # Act
        bot = TelegramBot(settings)

        # Assert
        assert bot.settings == settings
        assert bot.dp is not None
        assert bot.storage is not None

    @patch("src.presentation.telegram.bot.Bot")
    async def test_set_bot_commands(self, mock_bot: MagicMock) -> None:
        """Test bot commands are set correctly."""
        # Arrange
        settings = Settings(
            telegram_bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            environment="test",
            database_url="sqlite:///:memory:",
            redis_url="redis://localhost:6379/0",
            hikerapi_key="test_key",
        )
        
        # Mock bot instance
        mock_bot_instance = AsyncMock()
        mock_bot.return_value = mock_bot_instance
        
        bot = TelegramBot(settings)
        bot.bot.set_my_commands = AsyncMock()

        # Act
        await bot._set_bot_commands()

        # Assert
        bot.bot.set_my_commands.assert_called_once()
        commands = bot.bot.set_my_commands.call_args[0][0]
        assert len(commands) == 6
        assert commands[0].command == "start"
        assert commands[1].command == "tariffs"

"""Tests for payment handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import CallbackQuery, User

from src.presentation.telegram.handlers.payment_handlers import (
    buy_subscription_command_callback,
    payment_stars_callback,
    payment_robokassa_callback,
    payment_crypto_callback,
    handle_buy_callback,
    robokassa_buy_callback,
    crypto_buy_callback,
    get_payment_method_keyboard,
    get_stars_plans_keyboard,
    get_robokassa_plans_keyboard,
    get_crypto_currency_keyboard,
    get_crypto_plans_keyboard,
)


@pytest.mark.asyncio
class TestPaymentHandlers:
    """Tests for payment handlers."""

    @pytest.fixture
    def mock_callback(self):
        """Create mock callback query."""
        callback = AsyncMock(spec=CallbackQuery)
        callback.from_user = User(id=123, is_bot=False, first_name="Test")
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        return callback

    async def test_buy_subscription_command_callback(self, mock_callback):
        """Test buy_subscription_command_callback."""
        await buy_subscription_command_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert mock_callback.message.edit_text.called or mock_callback.message.answer.called

    async def test_payment_stars_callback(self, mock_callback):
        """Test payment_stars_callback."""
        await payment_stars_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert "Stars" in str(mock_callback.message.edit_text.call_args or mock_callback.message.answer.call_args)

    async def test_payment_robokassa_callback(self, mock_callback):
        """Test payment_robokassa_callback."""
        await payment_robokassa_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert "карт" in str(mock_callback.message.edit_text.call_args or mock_callback.message.answer.call_args)

    async def test_payment_crypto_callback(self, mock_callback):
        """Test payment_crypto_callback."""
        await payment_crypto_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert "CryptoBot" in str(mock_callback.message.edit_text.call_args or mock_callback.message.answer.call_args)

    async def test_handle_buy_callback_valid_plan(self, mock_callback, mock_container):
        """Test handle_buy_callback with valid plan."""
        mock_callback.data = "buy_1m"
        mock_callback.bot = AsyncMock()
        mock_callback.bot.send_invoice = AsyncMock()
        
        # Setup mocks
        mock_use_cases = mock_container.get_use_cases.return_value
        mock_create_payment = AsyncMock()
        mock_create_payment.execute = AsyncMock(return_value=MagicMock(id="payment_id"))
        mock_use_cases.create_payment = mock_create_payment
        
        await handle_buy_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()

    async def test_handle_buy_callback_invalid_plan(self, mock_callback, mock_container):
        """Test handle_buy_callback with invalid plan."""
        mock_callback.data = "buy_invalid"
        
        await handle_buy_callback(mock_callback)
        
        mock_callback.answer.assert_called_with("❌ Неверный тариф", show_alert=True)

    async def test_robokassa_buy_callback(self, mock_callback):
        """Test robokassa_buy_callback."""
        mock_callback.data = "robokassa_buy_1m"
        
        await robokassa_buy_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert mock_callback.message.edit_text.called or mock_callback.message.answer.called

    async def test_crypto_buy_callback_ton(self, mock_callback):
        """Test crypto_buy_callback for TON."""
        mock_callback.data = "crypto_ton_buy_1m"
        
        await crypto_buy_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert mock_callback.message.edit_text.called or mock_callback.message.answer.called

    async def test_crypto_buy_callback_usdt(self, mock_callback):
        """Test crypto_buy_callback for USDT."""
        mock_callback.data = "crypto_usdt_buy_1m"
        
        await crypto_buy_callback(mock_callback)
        
        mock_callback.answer.assert_called_once()
        assert mock_callback.message.edit_text.called or mock_callback.message.answer.called

    def test_get_payment_method_keyboard(self):
        """Test get_payment_method_keyboard."""
        keyboard = get_payment_method_keyboard()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 4  # 3 methods + back

    def test_get_stars_plans_keyboard(self):
        """Test get_stars_plans_keyboard."""
        keyboard = get_stars_plans_keyboard()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 5  # 4 plans + back

    def test_get_robokassa_plans_keyboard(self):
        """Test get_robokassa_plans_keyboard."""
        keyboard = get_robokassa_plans_keyboard()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 5  # 4 plans + back

    def test_get_crypto_currency_keyboard(self):
        """Test get_crypto_currency_keyboard."""
        keyboard = get_crypto_currency_keyboard()
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 3  # 2 currencies + back

    def test_get_crypto_plans_keyboard_ton(self):
        """Test get_crypto_plans_keyboard for TON."""
        keyboard = get_crypto_plans_keyboard("ton")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 5  # 4 plans + back

    def test_get_crypto_plans_keyboard_usdt(self):
        """Test get_crypto_plans_keyboard for USDT."""
        keyboard = get_crypto_plans_keyboard("usdt")
        
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 5  # 4 plans + back

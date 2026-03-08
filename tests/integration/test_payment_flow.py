"""Integration tests for payment flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from src.presentation.telegram.handlers.payment_handlers import (
    buy_subscription_command_callback,
    payment_stars_callback,
    handle_buy_callback,
    successful_payment_callback,
)


@pytest.mark.asyncio
class TestPaymentMenuFlow:
    """Test payment menu flow."""
    
    async def test_buy_subscription_shows_methods(self):
        """Test that buy subscription shows payment methods."""
        # Mock callback
        callback = AsyncMock()
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        
        await buy_subscription_command_callback(callback)
        
        # Verify callback was answered
        callback.answer.assert_called_once()
        
        # Verify payment methods were shown
        callback.message.edit_text.assert_called_once()
        call_args = callback.message.edit_text.call_args
        assert "Telegram Stars" in call_args[0][0]
        assert "Банковская карта" in call_args[0][0]
        assert "CryptoBot" in call_args[0][0]
    
    async def test_payment_stars_shows_plans(self):
        """Test that Stars payment shows plans."""
        # Mock callback
        callback = AsyncMock()
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.edit_text = AsyncMock()
        callback.answer = AsyncMock()
        
        await payment_stars_callback(callback)
        
        # Verify plans were shown
        callback.message.edit_text.assert_called_once()
        call_args = callback.message.edit_text.call_args
        assert "Выберите период подписки" in call_args[0][0]
        # Check keyboard has plans
        keyboard = call_args[1]["reply_markup"]
        keyboard_text = str(keyboard.inline_keyboard)
        assert "299" in keyboard_text


@pytest.mark.asyncio
class TestPaymentCreationFlow:
    """Test payment creation flow."""
    
    async def test_handle_buy_creates_payment(self):
        """Test that buy handler creates payment."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "buy_1m"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.message.answer = AsyncMock()
        callback.answer = AsyncMock()
        callback.bot = AsyncMock()
        callback.bot.send_invoice = AsyncMock()
        
        # Mock payment DTO
        from src.application.payment.dtos import PaymentDTO
        payment = PaymentDTO(
            id=uuid4(),
            user_id=123,
            amount=299.0,
            currency="STARS",
            method="TELEGRAM_STARS",
            status="PENDING",
            transaction_id=None,
            failure_reason=None,
            refund_amount=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        
        # Mock Use Cases
        with patch("src.presentation.telegram.handlers.payment_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_create_payment = AsyncMock()
            mock_create_payment.execute = AsyncMock(return_value=payment)
            mock_use_cases.create_payment = mock_create_payment
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await handle_buy_callback(callback)
            
            # Verify payment was created
            mock_create_payment.execute.assert_called_once()
            
            # Verify invoice was sent
            callback.bot.send_invoice.assert_called_once()
            
            # Verify success message
            callback.message.answer.assert_called_once()
            call_args = callback.message.answer.call_args
            assert "Счёт отправлен" in call_args[0][0]
    
    async def test_handle_buy_invalid_plan(self):
        """Test buy handler with invalid plan."""
        # Mock callback
        callback = AsyncMock()
        callback.data = "buy_invalid"
        callback.from_user = MagicMock(id=123)
        callback.message = AsyncMock()
        callback.answer = AsyncMock()
        
        # Mock container
        with patch("src.presentation.telegram.handlers.payment_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await handle_buy_callback(callback)
        
        # Verify error was shown
        callback.answer.assert_called()
        # Check if show_alert was used in any call
        calls = callback.answer.call_args_list
        assert any("show_alert" in str(call) for call in calls)


@pytest.mark.asyncio
class TestPaymentCompletionFlow:
    """Test payment completion flow."""
    
    async def test_successful_payment_activates_subscription(self):
        """Test that successful payment activates subscription."""
        # Mock message
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.successful_payment = MagicMock(
            telegram_payment_charge_id="charge_123",
            provider_payment_charge_id="provider_123",
            invoice_payload=str(uuid4()),
        )
        message.answer = AsyncMock()
        
        # Mock payment DTO with metadata attribute
        from src.application.payment.dtos import PaymentDTO
        payment = PaymentDTO(
            id=uuid4(),
            user_id=123,
            amount=299.0,
            currency="STARS",
            method="TELEGRAM_STARS",
            status="COMPLETED",
            transaction_id="charge_123",
            failure_reason=None,
            refund_amount=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        # Add metadata as attribute
        payment.metadata = {"plan_code": "1m", "days": 30}
        
        # Mock subscription DTO
        from src.application.subscription.dtos import SubscriptionDTO
        subscription = SubscriptionDTO(
            id=1,
            user_id=123,
            subscription_type="PREMIUM",
            status="ACTIVE",
            start_date=datetime.now().isoformat(),
            end_date=(datetime.now() + timedelta(days=30)).isoformat(),
            days_remaining=30,
            is_active=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        # Add end_date as datetime for formatting
        subscription.end_date = datetime.now() + timedelta(days=30)
        
        # Mock Use Cases
        with patch("src.presentation.telegram.handlers.payment_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_complete_payment = AsyncMock()
            mock_complete_payment.execute = AsyncMock(return_value=payment)
            mock_use_cases.complete_payment = mock_complete_payment
            
            mock_create_subscription = AsyncMock()
            mock_create_subscription.execute = AsyncMock(return_value=subscription)
            mock_use_cases.create_subscription = mock_create_subscription
            
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await successful_payment_callback(message)
            
            # Verify payment was completed
            mock_complete_payment.execute.assert_called_once()
            
            # Verify subscription was created
            mock_create_subscription.execute.assert_called_once()
            
            # Verify success message
            message.answer.assert_called_once()
            call_args = message.answer.call_args
            assert "успешна" in call_args[0][0].lower() or "активирована" in call_args[0][0].lower()
    
    async def test_successful_payment_error_handling(self):
        """Test successful payment with error."""
        # Mock message
        message = AsyncMock()
        message.from_user = MagicMock(id=123)
        message.successful_payment = MagicMock(
            telegram_payment_charge_id="charge_123",
            provider_payment_charge_id="provider_123",
            invoice_payload=str(uuid4()),
        )
        message.answer = AsyncMock()
        
        # Mock Use Cases to raise error
        with patch("src.presentation.telegram.handlers.payment_handlers.get_container") as mock_container:
            mock_use_cases = MagicMock()
            mock_use_cases.complete_payment = AsyncMock(side_effect=Exception("DB Error"))
            mock_container.return_value.get_use_cases.return_value = mock_use_cases
            
            await successful_payment_callback(message)
            
            # Verify error message
            message.answer.assert_called_once()
            call_args = message.answer.call_args
            assert "ошибка" in call_args[0][0].lower()
            assert "поддержку" in call_args[0][0].lower()

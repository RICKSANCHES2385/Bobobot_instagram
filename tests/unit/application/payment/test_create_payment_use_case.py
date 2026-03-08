"""Tests for CreatePaymentUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.payment.use_cases.create_payment import CreatePaymentUseCase
from src.application.payment.dtos import CreatePaymentCommand
from src.domain.payment.exceptions import InvalidPaymentAmountException


@pytest.fixture
def payment_repository():
    """Create mock payment repository."""
    return AsyncMock()


@pytest.fixture
def use_case(payment_repository):
    """Create use case instance."""
    return CreatePaymentUseCase(payment_repository=payment_repository)


@pytest.mark.asyncio
async def test_create_payment_success(use_case, payment_repository):
    """Test successful payment creation."""
    # Arrange
    command = CreatePaymentCommand(
        user_id=123,
        amount=100.0,
        currency="RUB",
        method="telegram_stars"
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.user_id == 123
    assert result.amount == 100.0
    assert result.currency == "RUB"
    assert result.method == "telegram_stars"
    assert result.status == "pending"
    assert result.transaction_id is None
    assert result.failure_reason is None
    assert result.refund_amount is None
    
    # Verify repository was called
    payment_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_create_payment_with_robokassa(use_case, payment_repository):
    """Test payment creation with Robokassa method."""
    # Arrange
    command = CreatePaymentCommand(
        user_id=456,
        amount=500.0,
        currency="RUB",
        method="robokassa"
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.method == "robokassa"
    assert result.status == "pending"


@pytest.mark.asyncio
async def test_create_payment_with_crypto_bot(use_case, payment_repository):
    """Test payment creation with CryptoBot method."""
    # Arrange
    command = CreatePaymentCommand(
        user_id=789,
        amount=10.0,
        currency="TON",
        method="crypto_bot"
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.method == "crypto_bot"
    assert result.currency == "TON"


@pytest.mark.asyncio
async def test_create_payment_with_zero_amount_raises_exception(use_case):
    """Test that creating payment with zero amount raises exception."""
    # Arrange
    command = CreatePaymentCommand(
        user_id=123,
        amount=0.0,
        currency="RUB",
        method="telegram_stars"
    )
    
    # Act & Assert
    with pytest.raises(InvalidPaymentAmountException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_create_payment_with_invalid_method_raises_exception(use_case):
    """Test that creating payment with invalid method raises exception."""
    # Arrange
    command = CreatePaymentCommand(
        user_id=123,
        amount=100.0,
        currency="RUB",
        method="invalid_method"
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid payment method"):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_create_payment_with_negative_amount_raises_exception(use_case):
    """Test that creating payment with negative amount raises exception."""
    # Arrange
    command = CreatePaymentCommand(
        user_id=123,
        amount=-100.0,
        currency="RUB",
        method="telegram_stars"
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        await use_case.execute(command)

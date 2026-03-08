"""Tests for RefundPaymentUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.payment.use_cases.refund_payment import RefundPaymentUseCase
from src.application.payment.dtos import RefundPaymentCommand
from src.domain.payment.aggregates.payment import Payment
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.payment.exceptions import (
    PaymentNotFoundException,
    InvalidPaymentStateException,
    InvalidPaymentAmountException
)
from src.domain.shared.value_objects.money import Money
from src.domain.user_management.value_objects.user_id import UserId


@pytest.fixture
def payment_repository():
    """Create mock payment repository."""
    return AsyncMock()


@pytest.fixture
def use_case(payment_repository):
    """Create use case instance."""
    return RefundPaymentUseCase(payment_repository=payment_repository)


@pytest.mark.asyncio
async def test_refund_payment_success(use_case, payment_repository):
    """Test successful payment refund."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()
    payment.complete(transaction_id="txn_123")
    payment_id = payment.id.value
    
    payment_repository.get_by_id.return_value = payment
    
    command = RefundPaymentCommand(
        payment_id=payment_id,
        refund_amount=100.0,
        reason="Customer request"
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.status == "refunded"
    assert result.refund_amount == 100.0
    assert result.failure_reason == "Customer request"
    
    # Verify repository was called
    payment_repository.get_by_id.assert_called_once()
    payment_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_refund_payment_partial(use_case, payment_repository):
    """Test partial payment refund."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()
    payment.complete()
    
    payment_repository.get_by_id.return_value = payment
    
    command = RefundPaymentCommand(
        payment_id=payment.id.value,
        refund_amount=50.0
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.status == "refunded"
    assert result.refund_amount == 50.0


@pytest.mark.asyncio
async def test_refund_payment_not_found_raises_exception(use_case, payment_repository):
    """Test that refunding non-existent payment raises exception."""
    # Arrange
    payment_id = uuid4()
    payment_repository.get_by_id.return_value = None
    
    command = RefundPaymentCommand(
        payment_id=payment_id,
        refund_amount=100.0
    )
    
    # Act & Assert
    with pytest.raises(PaymentNotFoundException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_refund_pending_payment_raises_exception(use_case, payment_repository):
    """Test that refunding pending payment raises exception."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    
    payment_repository.get_by_id.return_value = payment
    
    command = RefundPaymentCommand(
        payment_id=payment.id.value,
        refund_amount=100.0
    )
    
    # Act & Assert
    with pytest.raises(InvalidPaymentStateException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_refund_excessive_amount_raises_exception(use_case, payment_repository):
    """Test that refunding more than payment amount raises exception."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()
    payment.complete()
    
    payment_repository.get_by_id.return_value = payment
    
    command = RefundPaymentCommand(
        payment_id=payment.id.value,
        refund_amount=150.0
    )
    
    # Act & Assert
    with pytest.raises(InvalidPaymentAmountException):
        await use_case.execute(command)

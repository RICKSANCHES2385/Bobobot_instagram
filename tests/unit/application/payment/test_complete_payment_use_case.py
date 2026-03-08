"""Tests for CompletePaymentUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.payment.use_cases.complete_payment import CompletePaymentUseCase
from src.application.payment.dtos import CompletePaymentCommand
from src.domain.payment.aggregates.payment import Payment
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.payment.exceptions import PaymentNotFoundException, InvalidPaymentStateException
from src.domain.shared.value_objects.money import Money
from src.domain.user_management.value_objects.user_id import UserId


@pytest.fixture
def payment_repository():
    """Create mock payment repository."""
    return AsyncMock()


@pytest.fixture
def use_case(payment_repository):
    """Create use case instance."""
    return CompletePaymentUseCase(payment_repository=payment_repository)


@pytest.mark.asyncio
async def test_complete_payment_success(use_case, payment_repository):
    """Test successful payment completion."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()
    payment_id = payment.id.value
    
    payment_repository.get_by_id.return_value = payment
    
    command = CompletePaymentCommand(
        payment_id=payment_id,
        transaction_id="txn_123"
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.status == "completed"
    assert result.transaction_id == "txn_123"
    assert result.id == payment_id
    
    # Verify repository was called
    payment_repository.get_by_id.assert_called_once()
    payment_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_complete_payment_without_transaction_id(use_case, payment_repository):
    """Test payment completion without transaction ID."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()
    
    payment_repository.get_by_id.return_value = payment
    
    command = CompletePaymentCommand(payment_id=payment.id.value)
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.status == "completed"
    assert result.transaction_id is None


@pytest.mark.asyncio
async def test_complete_payment_not_found_raises_exception(use_case, payment_repository):
    """Test that completing non-existent payment raises exception."""
    # Arrange
    payment_id = uuid4()
    payment_repository.get_by_id.return_value = None
    
    command = CompletePaymentCommand(payment_id=payment_id)
    
    # Act & Assert
    with pytest.raises(PaymentNotFoundException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_complete_pending_payment_raises_exception(use_case, payment_repository):
    """Test that completing pending payment raises exception."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    # Not processed yet
    
    payment_repository.get_by_id.return_value = payment
    
    command = CompletePaymentCommand(payment_id=payment.id.value)
    
    # Act & Assert
    with pytest.raises(InvalidPaymentStateException):
        await use_case.execute(command)

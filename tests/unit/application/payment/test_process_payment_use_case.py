"""Tests for ProcessPaymentUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.payment.use_cases.process_payment import ProcessPaymentUseCase
from src.application.payment.dtos import ProcessPaymentCommand
from src.domain.payment.aggregates.payment import Payment
from src.domain.payment.value_objects.payment_id import PaymentId
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
    return ProcessPaymentUseCase(payment_repository=payment_repository)


@pytest.mark.asyncio
async def test_process_payment_success(use_case, payment_repository):
    """Test successful payment processing."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment_id = payment.id.value
    
    payment_repository.get_by_id.return_value = payment
    
    command = ProcessPaymentCommand(payment_id=payment_id)
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.status == "processing"
    assert result.id == payment_id
    
    # Verify repository was called
    payment_repository.get_by_id.assert_called_once()
    payment_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_process_payment_not_found_raises_exception(use_case, payment_repository):
    """Test that processing non-existent payment raises exception."""
    # Arrange
    payment_id = uuid4()
    payment_repository.get_by_id.return_value = None
    
    command = ProcessPaymentCommand(payment_id=payment_id)
    
    # Act & Assert
    with pytest.raises(PaymentNotFoundException):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_process_already_processing_payment_raises_exception(use_case, payment_repository):
    """Test that processing already processing payment raises exception."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()  # Already processing
    
    payment_repository.get_by_id.return_value = payment
    
    command = ProcessPaymentCommand(payment_id=payment.id.value)
    
    # Act & Assert
    with pytest.raises(InvalidPaymentStateException):
        await use_case.execute(command)

"""Tests for GetPaymentStatusUseCase."""
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.application.payment.use_cases.get_payment_status import GetPaymentStatusUseCase
from src.domain.payment.aggregates.payment import Payment
from src.domain.payment.value_objects.payment_method import PaymentMethod
from src.domain.payment.exceptions import PaymentNotFoundException
from src.domain.shared.value_objects.money import Money
from src.domain.user_management.value_objects.user_id import UserId


@pytest.fixture
def payment_repository():
    """Create mock payment repository."""
    return AsyncMock()


@pytest.fixture
def use_case(payment_repository):
    """Create use case instance."""
    return GetPaymentStatusUseCase(payment_repository=payment_repository)


@pytest.mark.asyncio
async def test_get_payment_status_success(use_case, payment_repository):
    """Test successful payment status retrieval."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment_id = payment.id.value
    
    payment_repository.get_by_id.return_value = payment
    
    # Act
    result = await use_case.execute(payment_id)
    
    # Assert
    assert result.id == payment_id
    assert result.user_id == 123
    assert result.amount == 100.0
    assert result.currency == "RUB"
    assert result.method == "telegram_stars"
    assert result.status == "pending"
    
    # Verify repository was called
    payment_repository.get_by_id.assert_called_once()


@pytest.mark.asyncio
async def test_get_payment_status_for_completed_payment(use_case, payment_repository):
    """Test getting status for completed payment."""
    # Arrange
    payment = Payment.create(
        user_id=UserId(value=123),
        amount=Money(amount=100.0, currency="RUB"),
        method=PaymentMethod.telegram_stars()
    )
    payment.process()
    payment.complete(transaction_id="txn_123")
    
    payment_repository.get_by_id.return_value = payment
    
    # Act
    result = await use_case.execute(payment.id.value)
    
    # Assert
    assert result.status == "completed"
    assert result.transaction_id == "txn_123"


@pytest.mark.asyncio
async def test_get_payment_status_not_found_raises_exception(use_case, payment_repository):
    """Test that getting status for non-existent payment raises exception."""
    # Arrange
    payment_id = uuid4()
    payment_repository.get_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(PaymentNotFoundException):
        await use_case.execute(payment_id)

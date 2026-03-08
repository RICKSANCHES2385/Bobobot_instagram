"""Tests for CancelSubscriptionUseCase."""
import pytest
from unittest.mock import AsyncMock
from src.application.subscription.use_cases.cancel_subscription import CancelSubscriptionUseCase
from src.application.subscription.dtos import CancelSubscriptionCommand
from src.domain.subscription.exceptions import SubscriptionNotFoundException
from src.domain.subscription.aggregates.subscription import Subscription
from src.domain.subscription.value_objects.subscription_id import SubscriptionId
from src.domain.subscription.value_objects.subscription_type import SubscriptionType
from src.domain.subscription.value_objects.subscription_period import SubscriptionPeriod
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.shared.value_objects.money import Money


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    """Create use case instance."""
    return CancelSubscriptionUseCase(subscription_repository=mock_repository)


@pytest.fixture
def sample_subscription():
    """Create sample subscription."""
    return Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )


async def test_cancel_subscription_success(use_case, mock_repository, sample_subscription):
    """Test cancelling subscription successfully."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = sample_subscription
    command = CancelSubscriptionCommand(user_id=123)
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.user_id == 123
    assert result.is_active is False
    mock_repository.save.assert_called_once()


async def test_cancel_subscription_not_found_raises(use_case, mock_repository):
    """Test cancelling non-existing subscription raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    command = CancelSubscriptionCommand(user_id=123)
    
    # Act & Assert
    with pytest.raises(SubscriptionNotFoundException):
        await use_case.execute(command)
    
    mock_repository.save.assert_not_called()


async def test_cancel_already_cancelled_raises(use_case, mock_repository, sample_subscription):
    """Test cancelling already cancelled subscription raises error."""
    # Arrange
    sample_subscription.cancel()
    mock_repository.get_active_by_user_id.return_value = sample_subscription
    command = CancelSubscriptionCommand(user_id=123)
    
    # Act & Assert
    with pytest.raises(ValueError):
        await use_case.execute(command)

"""Tests for RenewSubscriptionUseCase."""
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timedelta
from src.application.subscription.use_cases.renew_subscription import RenewSubscriptionUseCase
from src.application.subscription.dtos import RenewSubscriptionCommand
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
    return RenewSubscriptionUseCase(subscription_repository=mock_repository)


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


async def test_renew_subscription_success(use_case, mock_repository, sample_subscription):
    """Test renewing subscription successfully."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = sample_subscription
    command = RenewSubscriptionCommand(user_id=123, days=30)
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.user_id == 123
    assert result.is_active is True
    mock_repository.save.assert_called_once()


async def test_renew_subscription_not_found_raises(use_case, mock_repository):
    """Test renewing non-existing subscription raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    command = RenewSubscriptionCommand(user_id=123, days=30)
    
    # Act & Assert
    with pytest.raises(SubscriptionNotFoundException):
        await use_case.execute(command)
    
    mock_repository.save.assert_not_called()


async def test_renew_subscription_invalid_days_raises(use_case, mock_repository, sample_subscription):
    """Test renewing subscription with invalid days raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = sample_subscription
    command = RenewSubscriptionCommand(user_id=123, days=0)
    
    # Act & Assert
    with pytest.raises(ValueError):
        await use_case.execute(command)

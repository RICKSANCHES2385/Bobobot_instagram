"""Tests for CheckSubscriptionStatusUseCase."""
import pytest
from unittest.mock import AsyncMock
from src.application.subscription.use_cases.check_subscription_status import (
    CheckSubscriptionStatusUseCase
)
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
    return CheckSubscriptionStatusUseCase(subscription_repository=mock_repository)


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


async def test_check_status_with_active_subscription(use_case, mock_repository, sample_subscription):
    """Test checking status with active subscription."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = sample_subscription
    
    # Act
    result = await use_case.execute(user_id=123)
    
    # Assert
    assert result.has_active_subscription is True
    assert result.days_remaining >= 29
    assert result.subscription_type == "BASIC"


async def test_check_status_without_subscription(use_case, mock_repository):
    """Test checking status without subscription."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    
    # Act
    result = await use_case.execute(user_id=123)
    
    # Assert
    assert result.has_active_subscription is False
    assert result.days_remaining == 0
    assert result.subscription_type is None

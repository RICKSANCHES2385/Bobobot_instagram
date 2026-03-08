"""Tests for GetSubscriptionUseCase."""
import pytest
from unittest.mock import AsyncMock
from src.application.subscription.use_cases.get_subscription import GetSubscriptionUseCase
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
    return GetSubscriptionUseCase(subscription_repository=mock_repository)


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


async def test_get_subscription_success(use_case, mock_repository, sample_subscription):
    """Test getting subscription successfully."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = sample_subscription
    
    # Act
    result = await use_case.execute(user_id=123)
    
    # Assert
    assert result.user_id == 123
    assert result.subscription_type == "BASIC"
    assert result.is_active is True


async def test_get_subscription_not_found_raises(use_case, mock_repository):
    """Test getting non-existing subscription raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    
    # Act & Assert
    with pytest.raises(SubscriptionNotFoundException):
        await use_case.execute(user_id=123)

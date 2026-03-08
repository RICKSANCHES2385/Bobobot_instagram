"""Tests for CreateSubscriptionUseCase."""
import pytest
from unittest.mock import AsyncMock
from src.application.subscription.use_cases.create_subscription import CreateSubscriptionUseCase
from src.application.subscription.dtos import CreateSubscriptionCommand
from src.domain.subscription.exceptions import SubscriptionAlreadyExistsException


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_repository):
    """Create use case instance."""
    return CreateSubscriptionUseCase(subscription_repository=mock_repository)


async def test_create_subscription_success(use_case, mock_repository):
    """Test creating subscription successfully."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    command = CreateSubscriptionCommand(
        user_id=123,
        subscription_type="BASIC",
        days=30
    )
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.user_id == 123
    assert result.subscription_type == "BASIC"
    assert result.is_active is True
    assert result.days_remaining >= 29
    mock_repository.save.assert_called_once()


async def test_create_subscription_already_exists_raises(use_case, mock_repository):
    """Test creating subscription when active one exists raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = AsyncMock()
    command = CreateSubscriptionCommand(
        user_id=123,
        subscription_type="BASIC",
        days=30
    )
    
    # Act & Assert
    with pytest.raises(SubscriptionAlreadyExistsException):
        await use_case.execute(command)
    
    mock_repository.save.assert_not_called()


async def test_create_subscription_invalid_type_raises(use_case, mock_repository):
    """Test creating subscription with invalid type raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    command = CreateSubscriptionCommand(
        user_id=123,
        subscription_type="INVALID",
        days=30
    )
    
    # Act & Assert
    with pytest.raises(ValueError):
        await use_case.execute(command)


async def test_create_subscription_invalid_days_raises(use_case, mock_repository):
    """Test creating subscription with invalid days raises error."""
    # Arrange
    mock_repository.get_active_by_user_id.return_value = None
    command = CreateSubscriptionCommand(
        user_id=123,
        subscription_type="BASIC",
        days=0
    )
    
    # Act & Assert
    with pytest.raises(ValueError):
        await use_case.execute(command)

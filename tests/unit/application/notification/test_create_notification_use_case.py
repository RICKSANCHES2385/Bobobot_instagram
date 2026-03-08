"""Tests for Create Notification Use Case."""

import pytest
from unittest.mock import AsyncMock

from src.application.notification.use_cases.create_notification import CreateNotificationUseCase
from src.application.notification.dtos.notification_dto import CreateNotificationDTO


@pytest.fixture
def mock_notification_repository():
    """Create mock notification repository."""
    return AsyncMock()


@pytest.fixture
def use_case(mock_notification_repository):
    """Create use case instance."""
    return CreateNotificationUseCase(mock_notification_repository)


@pytest.mark.asyncio
class TestCreateNotificationUseCase:
    """Test create notification use case."""

    async def test_create_notification(self, use_case, mock_notification_repository):
        """Test creating notification."""
        # Arrange
        dto = CreateNotificationDTO(
            user_id="123456789",
            notification_type="content_update",
            title="New Post",
            message="User posted a new photo",
            priority="high",
            data={"post_id": "abc123"},
        )

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.user_id == "123456789"
        assert result.notification_type == "content_update"
        assert result.title == "New Post"
        assert result.message == "User posted a new photo"
        assert result.priority == "high"
        assert result.status == "pending"
        assert result.data["post_id"] == "abc123"
        mock_notification_repository.save.assert_called_once()

    async def test_create_notification_default_priority(self, use_case, mock_notification_repository):
        """Test creating notification with default priority."""
        # Arrange
        dto = CreateNotificationDTO(
            user_id="123456789",
            notification_type="system_message",
            title="System",
            message="System message",
        )

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.priority == "normal"
        mock_notification_repository.save.assert_called_once()

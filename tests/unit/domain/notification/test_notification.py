"""Tests for Notification Aggregate."""

import pytest

from src.domain.notification.aggregates.notification import Notification
from src.domain.notification.value_objects.notification_id import NotificationId
from src.domain.notification.value_objects.notification_type import NotificationType, NotificationTypeEnum
from src.domain.notification.value_objects.notification_priority import NotificationPriority, NotificationPriorityEnum
from src.domain.notification.events.notification_events import (
    NotificationCreatedEvent,
    NotificationSentEvent,
    NotificationFailedEvent,
    NotificationCancelledEvent,
)


class TestNotification:
    """Test notification aggregate."""

    def test_create_notification(self):
        """Test creating notification."""
        # Act
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="New Post",
            message="User posted a new photo",
            priority=NotificationPriority(NotificationPriorityEnum.HIGH),
            data={"post_id": "abc123"},
        )

        # Assert
        assert notification.user_id == "123456789"
        assert notification.notification_type.is_content_update()
        assert notification.title == "New Post"
        assert notification.message == "User posted a new photo"
        assert notification.priority.is_high()
        assert notification.data["post_id"] == "abc123"
        assert notification.status.is_pending()
        assert len(notification.domain_events) == 1
        assert isinstance(notification.domain_events[0], NotificationCreatedEvent)

    def test_create_notification_default_priority(self):
        """Test creating notification with default priority."""
        # Act
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.SYSTEM_MESSAGE),
            title="System",
            message="System message",
        )

        # Assert
        assert notification.priority.is_normal()

    def test_mark_as_sent(self):
        """Test marking notification as sent."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test message",
        )
        notification.clear_domain_events()

        # Act
        notification.mark_as_sent()

        # Assert
        assert notification.status.is_sent()
        assert notification.sent_at is not None
        assert len(notification.domain_events) == 1
        assert isinstance(notification.domain_events[0], NotificationSentEvent)

    def test_mark_as_sent_not_pending(self):
        """Test marking non-pending notification as sent."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test",
        )
        notification.mark_as_sent()

        # Act & Assert
        with pytest.raises(ValueError, match="pending"):
            notification.mark_as_sent()

    def test_mark_as_failed(self):
        """Test marking notification as failed."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test",
        )
        notification.clear_domain_events()

        # Act
        notification.mark_as_failed("Network error")

        # Assert
        assert notification.status.is_failed()
        assert notification.failed_at is not None
        assert notification.error_message == "Network error"
        assert notification.retry_count == 1
        assert len(notification.domain_events) == 1
        assert isinstance(notification.domain_events[0], NotificationFailedEvent)

    def test_cancel_notification(self):
        """Test cancelling notification."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test",
        )
        notification.clear_domain_events()

        # Act
        notification.cancel()

        # Assert
        assert notification.status.is_cancelled()
        assert len(notification.domain_events) == 1
        assert isinstance(notification.domain_events[0], NotificationCancelledEvent)

    def test_can_retry(self):
        """Test checking if notification can be retried."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test",
        )

        # Act & Assert - not failed yet
        assert not notification.can_retry()

        # Fail once (retry_count = 1)
        notification.mark_as_failed("Error 1")
        assert notification.can_retry()  # 1 < 3

        # Fail twice (retry_count = 2)
        notification.retry()
        notification.mark_as_failed("Error 2")
        assert notification.can_retry()  # 2 < 3

        # Fail three times (retry_count = 3, max retries reached)
        notification.retry()
        notification.mark_as_failed("Error 3")
        assert not notification.can_retry()  # 3 < 3 is False

    def test_retry_notification(self):
        """Test retrying notification."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test",
        )
        notification.mark_as_failed("Error")

        # Act
        notification.retry()

        # Assert
        assert notification.status.is_pending()
        assert notification.error_message is None

    def test_retry_notification_cannot_retry(self):
        """Test retrying notification that cannot be retried."""
        # Arrange
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id="123456789",
            notification_type=NotificationType(NotificationTypeEnum.CONTENT_UPDATE),
            title="Test",
            message="Test",
        )
        notification.mark_as_sent()

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot retry"):
            notification.retry()

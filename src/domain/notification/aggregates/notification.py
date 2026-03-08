"""Notification Aggregate."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from src.domain.shared.entities.base import AggregateRoot
from src.domain.notification.value_objects.notification_id import NotificationId
from src.domain.notification.value_objects.notification_type import NotificationType, NotificationTypeEnum
from src.domain.notification.value_objects.notification_status import NotificationStatus, NotificationStatusEnum
from src.domain.notification.value_objects.notification_priority import NotificationPriority, NotificationPriorityEnum
from src.domain.notification.events.notification_events import (
    NotificationCreatedEvent,
    NotificationSentEvent,
    NotificationFailedEvent,
    NotificationCancelledEvent,
)


@dataclass(eq=False)
class Notification(AggregateRoot):
    """Notification aggregate root."""

    notification_id: NotificationId = None
    user_id: str = None  # Telegram user ID
    notification_type: NotificationType = None
    status: NotificationStatus = None
    priority: NotificationPriority = None
    title: str = None
    message: str = None
    data: Optional[Dict[str, Any]] = None  # Additional data
    sent_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    @staticmethod
    def create(
        notification_id: NotificationId,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> "Notification":
        """Create new notification.
        
        Args:
            notification_id: Notification ID
            user_id: Telegram user ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority (default: NORMAL)
            data: Additional data
            
        Returns:
            Notification instance
        """
        if priority is None:
            priority = NotificationPriority(NotificationPriorityEnum.NORMAL)

        notification = Notification(
            id=notification_id.value,
            notification_id=notification_id,
            user_id=user_id,
            notification_type=notification_type,
            status=NotificationStatus(NotificationStatusEnum.PENDING),
            priority=priority,
            title=title,
            message=message,
            data=data or {},
            retry_count=0,
        )

        notification.add_domain_event(
            NotificationCreatedEvent(
                notification_id=notification_id.value,
                user_id=user_id,
                notification_type=notification_type.value.value,
                priority=priority.value.value,
            )
        )

        return notification

    def mark_as_sent(self) -> None:
        """Mark notification as sent."""
        if not self.status.is_pending():
            raise ValueError("Can only mark pending notifications as sent")

        self.status = NotificationStatus(NotificationStatusEnum.SENT)
        self.sent_at = datetime.utcnow()
        self._touch()

        self.add_domain_event(
            NotificationSentEvent(
                notification_id=self.notification_id.value,
                user_id=self.user_id,
                sent_at=self.sent_at,
            )
        )

    def mark_as_failed(self, error_message: str) -> None:
        """Mark notification as failed.
        
        Args:
            error_message: Error message
        """
        if self.status.is_final():
            raise ValueError("Cannot mark final notification as failed")

        self.status = NotificationStatus(NotificationStatusEnum.FAILED)
        self.failed_at = datetime.utcnow()
        self.error_message = error_message
        self.retry_count += 1
        self._touch()

        self.add_domain_event(
            NotificationFailedEvent(
                notification_id=self.notification_id.value,
                user_id=self.user_id,
                error_message=error_message,
                retry_count=self.retry_count,
            )
        )

    def cancel(self) -> None:
        """Cancel notification."""
        if self.status.is_final():
            raise ValueError("Cannot cancel final notification")

        self.status = NotificationStatus(NotificationStatusEnum.CANCELLED)
        self._touch()

        self.add_domain_event(
            NotificationCancelledEvent(
                notification_id=self.notification_id.value,
                user_id=self.user_id,
            )
        )

    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.status.is_failed() and
            self.retry_count < self.max_retries
        )

    def retry(self) -> None:
        """Retry sending notification."""
        if not self.can_retry():
            raise ValueError("Cannot retry notification")

        self.status = NotificationStatus(NotificationStatusEnum.PENDING)
        self.error_message = None
        self._touch()

    def __str__(self) -> str:
        """String representation."""
        return f"Notification {self.notification_id} ({self.notification_type}) - {self.status}"

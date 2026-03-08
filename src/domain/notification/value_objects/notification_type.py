"""Notification Type Value Object."""

from dataclasses import dataclass
from enum import Enum


class NotificationTypeEnum(str, Enum):
    """Notification type enumeration."""
    CONTENT_UPDATE = "content_update"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    SYSTEM_MESSAGE = "system_message"


@dataclass(frozen=True)
class NotificationType:
    """Notification type value object."""

    value: NotificationTypeEnum

    def is_content_update(self) -> bool:
        """Check if notification is content update."""
        return self.value == NotificationTypeEnum.CONTENT_UPDATE

    def is_subscription_related(self) -> bool:
        """Check if notification is subscription related."""
        return self.value in (
            NotificationTypeEnum.SUBSCRIPTION_EXPIRING,
            NotificationTypeEnum.SUBSCRIPTION_EXPIRED,
        )

    def is_payment_related(self) -> bool:
        """Check if notification is payment related."""
        return self.value in (
            NotificationTypeEnum.PAYMENT_SUCCESS,
            NotificationTypeEnum.PAYMENT_FAILED,
        )

    def is_system_message(self) -> bool:
        """Check if notification is system message."""
        return self.value == NotificationTypeEnum.SYSTEM_MESSAGE

    def __str__(self) -> str:
        """String representation."""
        return self.value.value

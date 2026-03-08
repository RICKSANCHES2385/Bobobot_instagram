"""Notification Status Value Object."""

from dataclasses import dataclass
from enum import Enum


class NotificationStatusEnum(str, Enum):
    """Notification status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class NotificationStatus:
    """Notification status value object."""

    value: NotificationStatusEnum

    def is_pending(self) -> bool:
        """Check if notification is pending."""
        return self.value == NotificationStatusEnum.PENDING

    def is_sent(self) -> bool:
        """Check if notification is sent."""
        return self.value == NotificationStatusEnum.SENT

    def is_failed(self) -> bool:
        """Check if notification is failed."""
        return self.value == NotificationStatusEnum.FAILED

    def is_cancelled(self) -> bool:
        """Check if notification is cancelled."""
        return self.value == NotificationStatusEnum.CANCELLED

    def is_final(self) -> bool:
        """Check if notification is in final state."""
        return self.value in (
            NotificationStatusEnum.SENT,
            NotificationStatusEnum.FAILED,
            NotificationStatusEnum.CANCELLED,
        )

    def __str__(self) -> str:
        """String representation."""
        return self.value.value

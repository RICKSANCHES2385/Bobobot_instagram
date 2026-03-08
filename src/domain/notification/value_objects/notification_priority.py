"""Notification Priority Value Object."""

from dataclasses import dataclass
from enum import Enum


class NotificationPriorityEnum(str, Enum):
    """Notification priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(frozen=True)
class NotificationPriority:
    """Notification priority value object."""

    value: NotificationPriorityEnum

    def is_urgent(self) -> bool:
        """Check if notification is urgent."""
        return self.value == NotificationPriorityEnum.URGENT

    def is_high(self) -> bool:
        """Check if notification is high priority."""
        return self.value == NotificationPriorityEnum.HIGH

    def is_normal(self) -> bool:
        """Check if notification is normal priority."""
        return self.value == NotificationPriorityEnum.NORMAL

    def is_low(self) -> bool:
        """Check if notification is low priority."""
        return self.value == NotificationPriorityEnum.LOW

    def get_order(self) -> int:
        """Get priority order (higher number = higher priority)."""
        order_map = {
            NotificationPriorityEnum.LOW: 1,
            NotificationPriorityEnum.NORMAL: 2,
            NotificationPriorityEnum.HIGH: 3,
            NotificationPriorityEnum.URGENT: 4,
        }
        return order_map[self.value]

    def __str__(self) -> str:
        """String representation."""
        return self.value.value

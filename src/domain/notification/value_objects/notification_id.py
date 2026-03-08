"""Notification ID Value Object."""

from dataclasses import dataclass
import uuid

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class NotificationId(BaseValueObject):
    """Notification ID value object."""

    value: str

    def __post_init__(self):
        """Validate notification ID."""
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Notification ID must be a non-empty string")
        if len(self.value) > 100:
            raise ValueError("Notification ID must not exceed 100 characters")

    @staticmethod
    def generate() -> "NotificationId":
        """Generate new notification ID."""
        return NotificationId(str(uuid.uuid4()))

    def __str__(self) -> str:
        """String representation."""
        return self.value

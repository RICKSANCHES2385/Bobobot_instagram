"""Tracking ID Value Object."""

from dataclasses import dataclass
import uuid

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TrackingId(BaseValueObject):
    """Tracking ID value object."""

    value: str

    def __post_init__(self):
        """Validate tracking ID."""
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Tracking ID must be a non-empty string")
        if len(self.value) > 100:
            raise ValueError("Tracking ID must not exceed 100 characters")

    @staticmethod
    def generate() -> "TrackingId":
        """Generate new tracking ID."""
        return TrackingId(str(uuid.uuid4()))

    def __str__(self) -> str:
        """String representation."""
        return self.value

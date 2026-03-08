"""Tracking Status Value Object."""

from dataclasses import dataclass
from enum import Enum

from src.domain.shared.value_objects.base import BaseValueObject


class TrackingStatusEnum(str, Enum):
    """Tracking status enumeration."""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass(frozen=True)
class TrackingStatus(BaseValueObject):
    """Tracking status value object."""

    value: TrackingStatusEnum

    def __post_init__(self):
        """Validate tracking status."""
        if not isinstance(self.value, TrackingStatusEnum):
            raise ValueError(f"Invalid tracking status: {self.value}")

    def is_active(self) -> bool:
        """Check if tracking is active."""
        return self.value == TrackingStatusEnum.ACTIVE

    def is_paused(self) -> bool:
        """Check if tracking is paused."""
        return self.value == TrackingStatusEnum.PAUSED

    def is_stopped(self) -> bool:
        """Check if tracking is stopped."""
        return self.value == TrackingStatusEnum.STOPPED

    def __str__(self) -> str:
        """String representation."""
        return self.value.value

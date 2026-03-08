"""Check Interval Value Object."""

from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class CheckInterval(BaseValueObject):
    """Check interval value object (in minutes)."""

    minutes: int

    def __post_init__(self):
        """Validate check interval."""
        if not isinstance(self.minutes, int):
            raise ValueError("Check interval must be an integer")
        if self.minutes < 5:
            raise ValueError("Check interval must be at least 5 minutes")
        if self.minutes > 1440:  # 24 hours
            raise ValueError("Check interval must not exceed 1440 minutes (24 hours)")

    def to_seconds(self) -> int:
        """Convert to seconds."""
        return self.minutes * 60

    def to_hours(self) -> float:
        """Convert to hours."""
        return self.minutes / 60

    def __str__(self) -> str:
        """String representation."""
        if self.minutes < 60:
            return f"{self.minutes} minutes"
        hours = self.minutes / 60
        return f"{hours:.1f} hours"

"""Following count value object."""

from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class FollowingCount(BaseValueObject):
    """Represents the number of accounts an Instagram user is following."""

    value: int

    def __post_init__(self) -> None:
        """Validate following count."""
        if not isinstance(self.value, int):
            raise ValueError("Following count must be an integer")
        if self.value < 0:
            raise ValueError("Following count cannot be negative")

    def __str__(self) -> str:
        """String representation."""
        return f"{self.value:,}"

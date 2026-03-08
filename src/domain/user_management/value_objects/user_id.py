"""User ID Value Object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """User ID value object."""

    value: int

    def __post_init__(self):
        """Validate user ID."""
        if not isinstance(self.value, int):
            raise ValueError("User ID must be an integer")
        if self.value <= 0:
            raise ValueError("User ID must be positive")

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)
    
    def __int__(self) -> int:
        """Integer representation."""
        return self.value

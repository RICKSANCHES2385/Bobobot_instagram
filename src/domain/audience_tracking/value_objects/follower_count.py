"""Follower count value object."""

from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class FollowerCount(BaseValueObject):
    """Represents the number of followers for an Instagram account."""

    value: int

    def __post_init__(self) -> None:
        """Validate follower count."""
        if not isinstance(self.value, int):
            raise ValueError("Follower count must be an integer")
        if self.value < 0:
            raise ValueError("Follower count cannot be negative")

    def exceeds_limit(self, limit: int = 100_000) -> bool:
        """Check if follower count exceeds the tracking limit.
        
        Business rule: Accounts with >100k followers cannot be tracked.
        
        Args:
            limit: Maximum allowed followers (default: 100,000)
            
        Returns:
            True if count exceeds limit
        """
        return self.value > limit

    def __str__(self) -> str:
        """String representation."""
        return f"{self.value:,}"

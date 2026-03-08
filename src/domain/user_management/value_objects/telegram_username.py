"""Telegram Username Value Object."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TelegramUsername:
    """Telegram username value object."""

    value: Optional[str]

    def __post_init__(self):
        """Validate username."""
        if self.value is not None:
            if not self.value:
                raise ValueError("Username cannot be empty string")
            if len(self.value) > 32:
                raise ValueError("Username is too long (max 32 characters)")
            if not self.value.replace("_", "").isalnum():
                raise ValueError("Username can only contain letters, numbers, and underscores")

    def __str__(self) -> str:
        """String representation."""
        return f"@{self.value}" if self.value else "No username"

    @property
    def is_set(self) -> bool:
        """Check if username is set."""
        return self.value is not None

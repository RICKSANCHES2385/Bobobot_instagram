"""Username Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class Username(BaseValueObject):
    """Telegram username."""
    
    value: str
    
    def _validate(self) -> None:
        """Validate username."""
        if not self.value:
            raise ValueError("Username cannot be empty")
        if len(self.value) > 32:
            raise ValueError("Username too long (max 32 characters)")
        if not self.value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers and underscores")

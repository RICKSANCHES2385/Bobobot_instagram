"""Telegram ID Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TelegramId(BaseValueObject):
    """Telegram user ID."""
    
    value: int
    
    def _validate(self) -> None:
        """Validate Telegram ID."""
        if self.value <= 0:
            raise ValueError("Telegram ID must be positive")

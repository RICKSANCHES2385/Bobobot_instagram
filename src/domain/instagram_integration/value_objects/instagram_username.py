"""Instagram Username Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class InstagramUsername(BaseValueObject):
    """Instagram username value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate Instagram username."""
        if not self.value:
            raise ValueError("Instagram username cannot be empty")
        
        if len(self.value) > 30:
            raise ValueError("Instagram username cannot exceed 30 characters")
        
        # Remove @ if present
        cleaned = self.value.lstrip("@")
        object.__setattr__(self, "value", cleaned)
    
    def __str__(self) -> str:
        """String representation."""
        return self.value

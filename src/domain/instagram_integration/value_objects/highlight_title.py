"""Highlight Title Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class HighlightTitle(BaseValueObject):
    """Instagram highlight title value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate highlight title."""
        # Title can be empty
        if self.value is None:
            object.__setattr__(self, "value", "")
        
        # Instagram highlight title max length
        if len(self.value) > 50:
            raise ValueError("Highlight title cannot exceed 50 characters")
    
    def __str__(self) -> str:
        """String representation."""
        return self.value if self.value else "Без названия"
    
    def is_empty(self) -> bool:
        """Check if title is empty."""
        return not self.value or self.value.strip() == ""

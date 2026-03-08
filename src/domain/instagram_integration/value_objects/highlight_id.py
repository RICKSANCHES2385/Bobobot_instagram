"""Highlight ID Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class HighlightId(BaseValueObject):
    """Instagram highlight ID value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate highlight ID."""
        if not self.value:
            raise ValueError("Highlight ID cannot be empty")
        
        # Ensure it's a string
        object.__setattr__(self, "value", str(self.value))
    
    def __str__(self) -> str:
        """String representation."""
        return self.value

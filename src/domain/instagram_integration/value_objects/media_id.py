"""Media ID Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class MediaId(BaseValueObject):
    """Instagram media ID value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate media ID."""
        if not self.value:
            raise ValueError("Media ID cannot be empty")
        
        # Ensure it's a string
        object.__setattr__(self, "value", str(self.value))
    
    def __str__(self) -> str:
        """String representation."""
        return self.value

"""Bio Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class Bio(BaseValueObject):
    """Instagram bio value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate bio."""
        # Bio can be empty
        if self.value is None:
            object.__setattr__(self, "value", "")
        
        # Instagram bio max length is 150 characters
        if len(self.value) > 150:
            raise ValueError("Bio cannot exceed 150 characters")
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def is_empty(self) -> bool:
        """Check if bio is empty."""
        return not self.value or self.value.strip() == ""

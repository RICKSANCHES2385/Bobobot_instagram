"""Caption Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class Caption(BaseValueObject):
    """Instagram caption value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate caption."""
        # Caption can be empty
        if self.value is None:
            object.__setattr__(self, "value", "")
        
        # Instagram caption max length is 2200 characters
        if len(self.value) > 2200:
            raise ValueError("Caption cannot exceed 2200 characters")
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def is_empty(self) -> bool:
        """Check if caption is empty."""
        return not self.value or self.value.strip() == ""
    
    def truncate(self, max_length: int = 200) -> str:
        """Truncate caption to specified length."""
        if len(self.value) <= max_length:
            return self.value
        return self.value[:max_length] + "..."

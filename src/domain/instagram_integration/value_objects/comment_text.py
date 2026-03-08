"""Comment Text Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class CommentText(BaseValueObject):
    """Instagram comment text value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate comment text."""
        # Comment can be empty (e.g., emoji-only)
        if self.value is None:
            object.__setattr__(self, "value", "")
        
        # Instagram comment max length
        if len(self.value) > 2200:
            raise ValueError("Comment text cannot exceed 2200 characters")
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def is_empty(self) -> bool:
        """Check if comment is empty."""
        return not self.value or self.value.strip() == ""
    
    def truncate(self, max_length: int = 100) -> str:
        """Truncate comment to specified length."""
        if len(self.value) <= max_length:
            return self.value
        return self.value[:max_length] + "..."

"""Media URL Value Object."""
from dataclasses import dataclass

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class MediaUrl(BaseValueObject):
    """Media URL value object."""
    
    value: str
    
    def __post_init__(self):
        """Validate media URL."""
        if not self.value:
            raise ValueError("Media URL cannot be empty")
        
        if not self.value.startswith(("http://", "https://")):
            raise ValueError("Media URL must start with http:// or https://")
    
    def __str__(self) -> str:
        """String representation."""
        return self.value

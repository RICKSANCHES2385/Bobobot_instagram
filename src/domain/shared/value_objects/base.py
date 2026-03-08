"""Base Value Object for DDD."""
from dataclasses import dataclass
from abc import ABC


@dataclass(frozen=True)
class BaseValueObject(ABC):
    """Base class for all Value Objects.
    
    Value Objects are immutable objects that are defined by their attributes.
    They have no identity and are compared by value equality.
    """
    
    def __post_init__(self) -> None:
        """Validate value object after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Override in subclasses to add validation.
        
        Raises:
            ValueError: If validation fails.
        """
        pass

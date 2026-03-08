"""Identifier Value Object."""
from dataclasses import dataclass
from typing import TypeVar, Generic
from uuid import UUID
from .base import BaseValueObject

T = TypeVar('T', int, str, UUID)


@dataclass(frozen=True)
class Identifier(BaseValueObject, Generic[T]):
    """Base class for identifiers.
    
    Identifiers are strongly-typed wrappers around primitive ID values.
    """
    
    value: T
    
    def _validate(self) -> None:
        """Validate identifier value."""
        if self.value is None:
            raise ValueError("Identifier value cannot be None")
    
    def __str__(self) -> str:
        """String representation."""
        return str(self.value)
    
    def __int__(self) -> int:
        """Integer representation (if applicable)."""
        if isinstance(self.value, int):
            return self.value
        raise TypeError(f"Cannot convert {type(self.value)} to int")

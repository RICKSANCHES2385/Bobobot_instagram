"""Specification Pattern for business rules."""
from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar('T')


class Specification(ABC):
    """Base class for specifications.
    
    Specifications encapsulate business rules that can be combined
    using logical operators (AND, OR, NOT).
    """
    
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if candidate satisfies the specification.
        
        Args:
            candidate: The object to check.
            
        Returns:
            True if specification is satisfied, False otherwise.
        """
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        """Combine with another specification using AND logic.
        
        Args:
            other: The other specification.
            
        Returns:
            Combined specification.
        """
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'Specification':
        """Combine with another specification using OR logic.
        
        Args:
            other: The other specification.
            
        Returns:
            Combined specification.
        """
        return OrSpecification(self, other)
    
    def not_(self) -> 'Specification':
        """Negate this specification.
        
        Returns:
            Negated specification.
        """
        return NotSpecification(self)


class AndSpecification(Specification):
    """AND combination of two specifications."""
    
    def __init__(self, left: Specification, right: Specification):
        """Initialize AND specification.
        
        Args:
            left: Left specification.
            right: Right specification.
        """
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if both specifications are satisfied."""
        return (
            self.left.is_satisfied_by(candidate) and 
            self.right.is_satisfied_by(candidate)
        )


class OrSpecification(Specification):
    """OR combination of two specifications."""
    
    def __init__(self, left: Specification, right: Specification):
        """Initialize OR specification.
        
        Args:
            left: Left specification.
            right: Right specification.
        """
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if either specification is satisfied."""
        return (
            self.left.is_satisfied_by(candidate) or 
            self.right.is_satisfied_by(candidate)
        )


class NotSpecification(Specification):
    """NOT negation of a specification."""
    
    def __init__(self, spec: Specification):
        """Initialize NOT specification.
        
        Args:
            spec: Specification to negate.
        """
        self.spec = spec
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        """Check if specification is not satisfied."""
        return not self.spec.is_satisfied_by(candidate)

"""Base Entity and Aggregate Root for DDD."""
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC
from typing import Any, List


@dataclass(eq=False)
class BaseEntity(ABC):
    """Base class for all Entities.
    
    Entities have identity and are compared by ID.
    They are mutable and track creation/update timestamps.
    """
    
    id: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __eq__(self, other: object) -> bool:
        """Equality by ID."""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash by ID."""
        return hash(self.id)
    
    def _touch(self) -> None:
        """Update updated_at timestamp."""
        self.updated_at = datetime.utcnow()


@dataclass(eq=False)
class AggregateRoot(BaseEntity):
    """Base class for Aggregate Roots.
    
    Aggregate Roots are entities that manage domain events
    and serve as entry points to aggregates.
    """
    
    _domain_events: List['DomainEvent'] = field(
        default_factory=list, init=False, repr=False
    )
    
    def add_domain_event(self, event: 'DomainEvent') -> None:
        """Add domain event to be published."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear all domain events."""
        self._domain_events.clear()
    
    @property
    def domain_events(self) -> List['DomainEvent']:
        """Get copy of domain events."""
        return self._domain_events.copy()


# Forward reference for type hints
from ..events.base import DomainEvent  # noqa: E402

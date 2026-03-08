"""Tests for AggregateRoot."""
import pytest
from dataclasses import dataclass
from src.domain.shared.entities.base import AggregateRoot
from src.domain.shared.events.base import DomainEvent


@dataclass(eq=False)
class TestAggregate(AggregateRoot):
    """Test aggregate."""
    name: str = "test"


@dataclass(frozen=True)
class TestEvent(DomainEvent):
    """Test event."""
    data: str = "test"


def test_aggregate_can_add_domain_events():
    """Aggregate should be able to add domain events."""
    aggregate = TestAggregate(id=1)
    event1 = TestEvent(data="event1")
    event2 = TestEvent(data="event2")
    
    aggregate.add_domain_event(event1)
    aggregate.add_domain_event(event2)
    
    assert len(aggregate.domain_events) == 2
    assert event1 in aggregate.domain_events
    assert event2 in aggregate.domain_events


def test_aggregate_can_clear_domain_events():
    """Aggregate should be able to clear domain events."""
    aggregate = TestAggregate(id=1)
    event = TestEvent(data="event")
    
    aggregate.add_domain_event(event)
    assert len(aggregate.domain_events) == 1
    
    aggregate.clear_domain_events()
    assert len(aggregate.domain_events) == 0


def test_aggregate_domain_events_are_copied():
    """Domain events property should return a copy."""
    aggregate = TestAggregate(id=1)
    event = TestEvent(data="event")
    
    aggregate.add_domain_event(event)
    events = aggregate.domain_events
    
    # Modifying the returned list should not affect the aggregate
    events.clear()
    assert len(aggregate.domain_events) == 1

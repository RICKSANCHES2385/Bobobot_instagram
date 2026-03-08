"""Tests for DomainEvent."""
import pytest
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class TestEvent(DomainEvent):
    """Test event."""
    data: str = "test"


def test_domain_event_is_immutable():
    """Domain event should be immutable."""
    event = TestEvent(data="test")
    
    with pytest.raises(Exception):  # FrozenInstanceError
        event.data = "modified"  # type: ignore


def test_domain_event_has_id():
    """Domain event should have a unique ID."""
    event1 = TestEvent(data="test1")
    event2 = TestEvent(data="test2")
    
    assert isinstance(event1.event_id, UUID)
    assert isinstance(event2.event_id, UUID)
    assert event1.event_id != event2.event_id


def test_domain_event_has_timestamp():
    """Domain event should have an occurred_at timestamp."""
    event = TestEvent(data="test")
    
    assert isinstance(event.occurred_at, datetime)
    assert event.occurred_at <= datetime.utcnow()

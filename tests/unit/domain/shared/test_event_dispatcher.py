"""Tests for EventDispatcher."""
import pytest
from dataclasses import dataclass
from src.domain.shared.events.base import DomainEvent
from src.domain.shared.events.event_dispatcher import EventDispatcher


@dataclass(frozen=True)
class UserCreatedEvent(DomainEvent):
    """Test event."""
    user_id: int = 0
    username: str = ""


@dataclass(frozen=True)
class UserDeletedEvent(DomainEvent):
    """Another test event."""
    user_id: int = 0


def test_event_dispatcher_register():
    """EventDispatcher should register handlers."""
    dispatcher = EventDispatcher()
    handler_called = []
    
    def handler(event: DomainEvent) -> None:
        handler_called.append(event)
    
    dispatcher.register(UserCreatedEvent, handler)
    
    assert dispatcher.handler_count(UserCreatedEvent) == 1


def test_event_dispatcher_dispatch():
    """EventDispatcher should dispatch events to handlers."""
    dispatcher = EventDispatcher()
    handler_called = []
    
    def handler(event: DomainEvent) -> None:
        handler_called.append(event)
    
    dispatcher.register(UserCreatedEvent, handler)
    event = UserCreatedEvent(user_id=1, username="test")
    
    dispatcher.dispatch(event)
    
    assert len(handler_called) == 1
    assert handler_called[0] == event


def test_event_dispatcher_multiple_handlers():
    """EventDispatcher should support multiple handlers for same event."""
    dispatcher = EventDispatcher()
    handler1_called = []
    handler2_called = []
    
    def handler1(event: DomainEvent) -> None:
        handler1_called.append(event)
    
    def handler2(event: DomainEvent) -> None:
        handler2_called.append(event)
    
    dispatcher.register(UserCreatedEvent, handler1)
    dispatcher.register(UserCreatedEvent, handler2)
    event = UserCreatedEvent(user_id=1, username="test")
    
    dispatcher.dispatch(event)
    
    assert len(handler1_called) == 1
    assert len(handler2_called) == 1


def test_event_dispatcher_different_event_types():
    """EventDispatcher should handle different event types separately."""
    dispatcher = EventDispatcher()
    created_called = []
    deleted_called = []
    
    def created_handler(event: DomainEvent) -> None:
        created_called.append(event)
    
    def deleted_handler(event: DomainEvent) -> None:
        deleted_called.append(event)
    
    dispatcher.register(UserCreatedEvent, created_handler)
    dispatcher.register(UserDeletedEvent, deleted_handler)
    
    created_event = UserCreatedEvent(user_id=1, username="test")
    deleted_event = UserDeletedEvent(user_id=1)
    
    dispatcher.dispatch(created_event)
    dispatcher.dispatch(deleted_event)
    
    assert len(created_called) == 1
    assert len(deleted_called) == 1
    assert created_called[0] == created_event
    assert deleted_called[0] == deleted_event


def test_event_dispatcher_clear():
    """EventDispatcher should clear all handlers."""
    dispatcher = EventDispatcher()
    
    def handler(event: DomainEvent) -> None:
        pass
    
    dispatcher.register(UserCreatedEvent, handler)
    assert dispatcher.handler_count(UserCreatedEvent) == 1
    
    dispatcher.clear()
    assert dispatcher.handler_count(UserCreatedEvent) == 0

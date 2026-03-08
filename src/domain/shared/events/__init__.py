"""Shared domain events."""

from .base import DomainEvent
from .event_dispatcher import EventDispatcher

__all__ = [
    "DomainEvent",
    "EventDispatcher",
]

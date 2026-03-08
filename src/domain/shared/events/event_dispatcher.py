"""Event Dispatcher for Domain Events."""
from typing import Dict, List, Type, Callable, Any
from .base import DomainEvent


EventHandler = Callable[[DomainEvent], None]


class EventDispatcher:
    """Event dispatcher for domain events.
    
    Manages registration and dispatching of domain event handlers.
    """
    
    def __init__(self) -> None:
        """Initialize event dispatcher."""
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = {}
    
    def register(
        self, 
        event_type: Type[DomainEvent], 
        handler: EventHandler
    ) -> None:
        """Register an event handler for a specific event type.
        
        Args:
            event_type: The type of event to handle.
            handler: The handler function to call when event is dispatched.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def dispatch(self, event: DomainEvent) -> None:
        """Dispatch an event to all registered handlers.
        
        Args:
            event: The event to dispatch.
        """
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
    
    def clear(self) -> None:
        """Clear all registered handlers."""
        self._handlers.clear()
    
    def handler_count(self, event_type: Type[DomainEvent]) -> int:
        """Get number of handlers for an event type.
        
        Args:
            event_type: The event type to check.
            
        Returns:
            Number of registered handlers.
        """
        return len(self._handlers.get(event_type, []))

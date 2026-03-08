"""Payment domain events."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ...shared.events.base import DomainEvent


@dataclass(frozen=True)
class PaymentCreated(DomainEvent):
    """Event raised when a payment is created."""
    
    payment_id: int = None
    user_id: int = None
    amount: float = None
    currency: str = None
    method: str = None
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "payment.created"


@dataclass(frozen=True)
class PaymentProcessing(DomainEvent):
    """Event raised when a payment starts processing."""
    
    payment_id: int = None
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "payment.processing"


@dataclass(frozen=True)
class PaymentCompleted(DomainEvent):
    """Event raised when a payment is completed."""
    
    payment_id: int = None
    transaction_id: Optional[str] = None
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "payment.completed"


@dataclass(frozen=True)
class PaymentFailed(DomainEvent):
    """Event raised when a payment fails."""
    
    payment_id: int = None
    reason: str = None
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "payment.failed"


@dataclass(frozen=True)
class PaymentCancelled(DomainEvent):
    """Event raised when a payment is cancelled."""
    
    payment_id: int = None
    reason: Optional[str] = None
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "payment.cancelled"


@dataclass(frozen=True)
class PaymentRefunded(DomainEvent):
    """Event raised when a payment is refunded."""
    
    payment_id: int = None
    refund_amount: float = None
    reason: Optional[str] = None
    
    @property
    def event_name(self) -> str:
        """Get event name."""
        return "payment.refunded"

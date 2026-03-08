"""Subscription Domain Events."""
from dataclasses import dataclass
from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class SubscriptionCreated(DomainEvent):
    """Subscription created event."""
    subscription_id: int = 0
    user_id: int = 0
    subscription_type: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class SubscriptionRenewed(DomainEvent):
    """Subscription renewed event."""
    subscription_id: int = 0
    user_id: int = 0
    old_end_date: str = ""
    new_end_date: str = ""
    days_added: int = 0


@dataclass(frozen=True)
class SubscriptionCancelled(DomainEvent):
    """Subscription cancelled event."""
    subscription_id: int = 0
    user_id: int = 0
    cancelled_at: str = ""


@dataclass(frozen=True)
class SubscriptionExpired(DomainEvent):
    """Subscription expired event."""
    subscription_id: int = 0
    user_id: int = 0
    expired_at: str = ""

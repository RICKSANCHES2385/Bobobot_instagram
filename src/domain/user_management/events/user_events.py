"""User Domain Events."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class UserRegisteredEvent(DomainEvent):
    """User registered event."""

    user_id: str = ""
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass(frozen=True)
class UserRoleChangedEvent(DomainEvent):
    """User role changed event."""

    user_id: str = ""
    old_role: str = ""
    new_role: str = ""


@dataclass(frozen=True)
class SubscriptionActivatedEvent(DomainEvent):
    """Subscription activated event."""

    user_id: str = ""
    expires_at: datetime = None
    is_trial: bool = False


@dataclass(frozen=True)
class SubscriptionExpiredEvent(DomainEvent):
    """Subscription expired event."""

    user_id: str = ""


@dataclass(frozen=True)
class SubscriptionCancelledEvent(DomainEvent):
    """Subscription cancelled event."""

    user_id: str = ""


@dataclass(frozen=True)
class UserActivityUpdatedEvent(DomainEvent):
    """User activity updated event."""

    user_id: str = ""
    last_activity_at: datetime = None

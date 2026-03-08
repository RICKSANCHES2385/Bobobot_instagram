"""Notification Domain Events."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class NotificationCreatedEvent(DomainEvent):
    """Notification created event."""

    notification_id: str = ""
    user_id: str = ""
    notification_type: str = ""
    priority: str = ""


@dataclass(frozen=True)
class NotificationSentEvent(DomainEvent):
    """Notification sent event."""

    notification_id: str = ""
    user_id: str = ""
    sent_at: datetime = None


@dataclass(frozen=True)
class NotificationFailedEvent(DomainEvent):
    """Notification failed event."""

    notification_id: str = ""
    user_id: str = ""
    error_message: str = ""
    retry_count: int = 0


@dataclass(frozen=True)
class NotificationCancelledEvent(DomainEvent):
    """Notification cancelled event."""

    notification_id: str = ""
    user_id: str = ""

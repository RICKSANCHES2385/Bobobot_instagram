"""Content Tracking Domain Events."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class TrackingStartedEvent(DomainEvent):
    """Event raised when tracking is started."""

    tracking_id: str = ""
    user_id: str = ""
    instagram_username: str = ""
    content_type: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class TrackingPausedEvent(DomainEvent):
    """Event raised when tracking is paused."""

    tracking_id: str = ""
    user_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class TrackingResumedEvent(DomainEvent):
    """Event raised when tracking is resumed."""

    tracking_id: str = ""
    user_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class TrackingStoppedEvent(DomainEvent):
    """Event raised when tracking is stopped."""

    tracking_id: str = ""
    user_id: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ContentUpdateDetectedEvent(DomainEvent):
    """Event raised when new content is detected."""

    tracking_id: str = ""
    user_id: str = ""
    instagram_username: str = ""
    content_type: str = ""
    content_id: str = ""
    content_url: str = ""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

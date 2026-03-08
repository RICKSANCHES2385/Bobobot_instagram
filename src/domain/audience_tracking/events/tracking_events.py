"""Audience tracking domain events."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class AudienceTrackingSubscriptionCreated:
    """Event raised when audience tracking subscription is created."""

    tracking_id: int
    user_id: int
    target_username: str
    target_user_id: str
    expires_at: datetime
    amount_paid: float
    currency: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AudienceTrackingSubscriptionExpired:
    """Event raised when audience tracking subscription expires."""

    tracking_id: int
    user_id: int
    target_username: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AudienceTrackingSubscriptionCancelled:
    """Event raised when audience tracking subscription is cancelled."""

    tracking_id: int
    user_id: int
    target_username: str
    reason: Optional[str] = None
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class FollowersChanged:
    """Event raised when follower count changes."""

    tracking_id: int
    user_id: int
    target_username: str
    old_count: int
    new_count: int
    difference: int
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class FollowingChanged:
    """Event raised when following count changes."""

    tracking_id: int
    user_id: int
    target_username: str
    old_count: int
    new_count: int
    difference: int
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AudienceTrackingSubscriptionRenewed:
    """Event raised when audience tracking subscription is renewed."""

    tracking_id: int
    user_id: int
    target_username: str
    new_expires_at: datetime
    amount_paid: float
    currency: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

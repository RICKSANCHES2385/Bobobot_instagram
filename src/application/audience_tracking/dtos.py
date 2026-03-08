"""Audience Tracking DTOs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CreateAudienceTrackingDTO:
    """DTO for creating audience tracking subscription."""

    user_id: int
    target_username: str
    target_user_id: str
    currency: str  # RUB, XTR, USDT, TON
    payment_id: Optional[int] = None
    duration_days: int = 30


@dataclass
class AudienceTrackingDTO:
    """DTO for audience tracking subscription."""

    tracking_id: int
    user_id: int
    target_username: str
    target_user_id: str
    is_active: bool
    expires_at: datetime
    auto_renew: bool
    amount_paid: float
    currency: str
    last_follower_count: Optional[int] = None
    last_following_count: Optional[int] = None
    last_checked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def days_remaining(self) -> int:
        """Calculate remaining days."""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)


@dataclass
class AudienceChangeDTO:
    """DTO for audience change notification."""

    tracking_id: int
    user_id: int
    target_username: str
    change_type: str  # "followers" or "following"
    old_count: int
    new_count: int
    difference: int
    timestamp: datetime


@dataclass
class RenewTrackingDTO:
    """DTO for renewing tracking subscription."""

    tracking_id: int
    currency: str
    payment_id: Optional[int] = None
    duration_days: int = 30

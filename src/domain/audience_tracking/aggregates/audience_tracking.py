"""Audience Tracking Aggregate Root."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from src.domain.shared.entities.base import AggregateRoot
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId
from src.domain.audience_tracking.value_objects.follower_count import FollowerCount
from src.domain.audience_tracking.value_objects.following_count import FollowingCount
from src.domain.audience_tracking.value_objects.tracking_price import TrackingPrice
from src.domain.audience_tracking.events.tracking_events import (
    AudienceTrackingSubscriptionCreated,
    AudienceTrackingSubscriptionExpired,
    AudienceTrackingSubscriptionCancelled,
    FollowersChanged,
    FollowingChanged,
    AudienceTrackingSubscriptionRenewed,
)


@dataclass(eq=False)
class AudienceTracking(AggregateRoot):
    """Audience Tracking aggregate root.
    
    Represents a paid subscription for tracking followers/following
    of a specific Instagram account.
    
    Business Rules:
    - Each tracked account requires a separate paid subscription
    - Price: 576 Stars or 129 RUB/month
    - Accounts with >100k followers cannot be tracked
    - Subscription expires after 30 days
    """

    tracking_id: Optional[TrackingId] = None
    user_id: int = None
    target_username: str = None
    target_user_id: str = None
    
    # Subscription status
    is_active: bool = True
    expires_at: Optional[datetime] = None
    auto_renew: bool = False
    
    # Payment information
    payment_id: Optional[int] = None
    amount_paid: float = None
    currency: str = None
    
    # Tracking data
    last_follower_count: Optional[FollowerCount] = None
    last_following_count: Optional[FollowingCount] = None
    last_checked_at: Optional[datetime] = None

    @staticmethod
    def create(
        user_id: int,
        target_username: str,
        target_user_id: str,
        price: TrackingPrice,
        payment_id: Optional[int] = None,
        duration_days: int = 30,
    ) -> "AudienceTracking":
        """Create new audience tracking subscription.
        
        Args:
            user_id: User ID who owns the subscription
            target_username: Instagram username to track
            target_user_id: Instagram user ID to track
            price: Subscription price
            payment_id: Associated payment ID
            duration_days: Subscription duration in days
            
        Returns:
            AudienceTracking instance
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not target_username or not target_username.strip():
            raise ValueError("Target username cannot be empty")
        
        if not target_user_id or not target_user_id.strip():
            raise ValueError("Target user ID cannot be empty")
        
        if duration_days <= 0:
            raise ValueError("Duration must be positive")

        expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        tracking = AudienceTracking(
            id=None,  # Will be set by repository
            user_id=user_id,
            target_username=target_username.strip(),
            target_user_id=target_user_id.strip(),
            is_active=True,
            expires_at=expires_at,
            payment_id=payment_id,
            amount_paid=float(price.amount),
            currency=price.currency,
            auto_renew=False,
        )

        # Event will be added after repository assigns ID
        return tracking

    def _raise_created_event(self) -> None:
        """Raise subscription created event (called after ID is assigned)."""
        if self.tracking_id is None:
            raise ValueError("Cannot raise event without tracking ID")
        
        self.add_domain_event(
            AudienceTrackingSubscriptionCreated(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
                target_username=self.target_username,
                target_user_id=self.target_user_id,
                expires_at=self.expires_at,
                amount_paid=self.amount_paid,
                currency=self.currency,
            )
        )

    def update_follower_count(self, new_count: FollowerCount) -> None:
        """Update follower count and raise event if changed.
        
        Args:
            new_count: New follower count
        """
        if not self.is_active:
            raise ValueError("Cannot update inactive subscription")
        
        if self.is_expired():
            raise ValueError("Cannot update expired subscription")

        old_count = self.last_follower_count
        self.last_follower_count = new_count
        self.last_checked_at = datetime.utcnow()
        self._touch()

        if old_count is not None and old_count.value != new_count.value:
            difference = new_count.value - old_count.value
            self.add_domain_event(
                FollowersChanged(
                    tracking_id=self.tracking_id.value,
                    user_id=self.user_id,
                    target_username=self.target_username,
                    old_count=old_count.value,
                    new_count=new_count.value,
                    difference=difference,
                )
            )

    def update_following_count(self, new_count: FollowingCount) -> None:
        """Update following count and raise event if changed.
        
        Args:
            new_count: New following count
        """
        if not self.is_active:
            raise ValueError("Cannot update inactive subscription")
        
        if self.is_expired():
            raise ValueError("Cannot update expired subscription")

        old_count = self.last_following_count
        self.last_following_count = new_count
        self.last_checked_at = datetime.utcnow()
        self._touch()

        if old_count is not None and old_count.value != new_count.value:
            difference = new_count.value - old_count.value
            self.add_domain_event(
                FollowingChanged(
                    tracking_id=self.tracking_id.value,
                    user_id=self.user_id,
                    target_username=self.target_username,
                    old_count=old_count.value,
                    new_count=new_count.value,
                    difference=difference,
                )
            )

    def renew(self, price: TrackingPrice, payment_id: Optional[int] = None, duration_days: int = 30) -> None:
        """Renew subscription.
        
        Args:
            price: Renewal price
            payment_id: Associated payment ID
            duration_days: Extension duration in days
        """
        if duration_days <= 0:
            raise ValueError("Duration must be positive")

        # Extend from current expiration or now, whichever is later
        base_time = max(self.expires_at, datetime.utcnow()) if self.expires_at else datetime.utcnow()
        self.expires_at = base_time + timedelta(days=duration_days)
        self.is_active = True
        self.payment_id = payment_id
        self.amount_paid = float(price.amount)
        self.currency = price.currency
        self._touch()

        self.add_domain_event(
            AudienceTrackingSubscriptionRenewed(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
                target_username=self.target_username,
                new_expires_at=self.expires_at,
                amount_paid=self.amount_paid,
                currency=self.currency,
            )
        )

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel subscription.
        
        Args:
            reason: Cancellation reason
        """
        if not self.is_active:
            raise ValueError("Subscription is already inactive")

        self.is_active = False
        self.auto_renew = False
        self._touch()

        self.add_domain_event(
            AudienceTrackingSubscriptionCancelled(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
                target_username=self.target_username,
                reason=reason,
            )
        )

    def expire(self) -> None:
        """Mark subscription as expired."""
        if not self.is_active:
            return

        self.is_active = False
        self._touch()

        self.add_domain_event(
            AudienceTrackingSubscriptionExpired(
                tracking_id=self.tracking_id.value,
                user_id=self.user_id,
                target_username=self.target_username,
            )
        )

    def enable_auto_renew(self) -> None:
        """Enable automatic renewal."""
        self.auto_renew = True
        self._touch()

    def disable_auto_renew(self) -> None:
        """Disable automatic renewal."""
        self.auto_renew = False
        self._touch()

    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        if self.expires_at is None:
            return True
        return datetime.utcnow() > self.expires_at

    def days_remaining(self) -> int:
        """Calculate remaining days for subscription."""
        if self.is_expired():
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def __str__(self) -> str:
        """String representation."""
        status = "active" if self.is_active and not self.is_expired() else "inactive"
        return f"AudienceTracking(user={self.user_id}, target=@{self.target_username}, status={status})"

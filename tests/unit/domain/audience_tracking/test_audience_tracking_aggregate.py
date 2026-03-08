"""Tests for AudienceTracking aggregate."""

import pytest
from datetime import datetime, timedelta

from src.domain.audience_tracking.aggregates.audience_tracking import AudienceTracking
from src.domain.audience_tracking.value_objects.tracking_price import TrackingPrice
from src.domain.audience_tracking.value_objects.follower_count import FollowerCount
from src.domain.audience_tracking.value_objects.following_count import FollowingCount
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId


class TestAudienceTrackingAggregate:
    """Test AudienceTracking aggregate root."""

    def test_create_tracking(self):
        """Test creating audience tracking subscription."""
        price = TrackingPrice.for_stars()
        
        tracking = AudienceTracking.create(
            user_id=123,
            target_username="testuser",
            target_user_id="456",
            price=price,
            payment_id=789,
            duration_days=30
        )
        
        assert tracking.user_id == 123
        assert tracking.target_username == "testuser"
        assert tracking.target_user_id == "456"
        assert tracking.is_active is True
        assert tracking.amount_paid == 576.0
        assert tracking.currency == "XTR"
        assert tracking.payment_id == 789
        assert tracking.expires_at is not None
        assert tracking.auto_renew is False

    def test_create_tracking_with_custom_duration(self):
        """Test creating tracking with custom duration."""
        price = TrackingPrice.for_rubles()
        
        tracking = AudienceTracking.create(
            user_id=123,
            target_username="testuser",
            target_user_id="456",
            price=price,
            duration_days=90
        )
        
        expected_expiry = datetime.utcnow() + timedelta(days=90)
        assert abs((tracking.expires_at - expected_expiry).total_seconds()) < 5

    def test_create_tracking_empty_username(self):
        """Test creating tracking with empty username."""
        price = TrackingPrice.for_stars()
        
        with pytest.raises(ValueError, match="Target username cannot be empty"):
            AudienceTracking.create(
                user_id=123,
                target_username="",
                target_user_id="456",
                price=price
            )

    def test_create_tracking_empty_user_id(self):
        """Test creating tracking with empty user ID."""
        price = TrackingPrice.for_stars()
        
        with pytest.raises(ValueError, match="Target user ID cannot be empty"):
            AudienceTracking.create(
                user_id=123,
                target_username="testuser",
                target_user_id="",
                price=price
            )

    def test_create_tracking_invalid_duration(self):
        """Test creating tracking with invalid duration."""
        price = TrackingPrice.for_stars()
        
        with pytest.raises(ValueError, match="Duration must be positive"):
            AudienceTracking.create(
                user_id=123,
                target_username="testuser",
                target_user_id="456",
                price=price,
                duration_days=0
            )

    def test_update_follower_count(self):
        """Test updating follower count."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        
        # First update - no event (no previous count)
        new_count = FollowerCount(1000)
        tracking.update_follower_count(new_count)
        
        assert tracking.last_follower_count == new_count
        assert tracking.last_checked_at is not None
        assert len(tracking.domain_events) == 0  # No event on first update
        
        # Second update - should raise event
        newer_count = FollowerCount(1100)
        tracking.update_follower_count(newer_count)
        
        assert tracking.last_follower_count == newer_count
        assert len(tracking.domain_events) == 1
        
        event = tracking.domain_events[0]
        assert event.__class__.__name__ == "FollowersChanged"
        assert event.old_count == 1000
        assert event.new_count == 1100
        assert event.difference == 100

    def test_update_following_count(self):
        """Test updating following count."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        
        # First update
        new_count = FollowingCount(500)
        tracking.update_following_count(new_count)
        
        assert tracking.last_following_count == new_count
        
        # Second update with decrease
        newer_count = FollowingCount(450)
        tracking.update_following_count(newer_count)
        
        assert len(tracking.domain_events) == 1
        
        event = tracking.domain_events[0]
        assert event.__class__.__name__ == "FollowingChanged"
        assert event.difference == -50

    def test_update_count_inactive_tracking(self):
        """Test updating count on inactive tracking."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        tracking.is_active = False
        
        with pytest.raises(ValueError, match="Cannot update inactive subscription"):
            tracking.update_follower_count(FollowerCount(1000))

    def test_update_count_expired_tracking(self):
        """Test updating count on expired tracking."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        tracking.expires_at = datetime.utcnow() - timedelta(days=1)
        
        with pytest.raises(ValueError, match="Cannot update expired subscription"):
            tracking.update_follower_count(FollowerCount(1000))

    def test_renew_subscription(self):
        """Test renewing subscription."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        
        old_expiry = tracking.expires_at
        price = TrackingPrice.for_rubles()
        
        tracking.renew(price=price, payment_id=999, duration_days=30)
        
        assert tracking.is_active is True
        assert tracking.expires_at > old_expiry
        assert tracking.payment_id == 999
        assert tracking.amount_paid == 129.0
        assert tracking.currency == "RUB"
        
        # Check event
        assert len(tracking.domain_events) == 1
        event = tracking.domain_events[0]
        assert event.__class__.__name__ == "AudienceTrackingSubscriptionRenewed"

    def test_cancel_subscription(self):
        """Test cancelling subscription."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        
        tracking.cancel(reason="User requested")
        
        assert tracking.is_active is False
        assert tracking.auto_renew is False
        
        # Check event
        assert len(tracking.domain_events) == 1
        event = tracking.domain_events[0]
        assert event.__class__.__name__ == "AudienceTrackingSubscriptionCancelled"
        assert event.reason == "User requested"

    def test_cancel_inactive_subscription(self):
        """Test cancelling already inactive subscription."""
        tracking = self._create_test_tracking()
        tracking.is_active = False
        
        with pytest.raises(ValueError, match="Subscription is already inactive"):
            tracking.cancel()

    def test_expire_subscription(self):
        """Test expiring subscription."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        
        tracking.expire()
        
        assert tracking.is_active is False
        
        # Check event
        assert len(tracking.domain_events) == 1
        event = tracking.domain_events[0]
        assert event.__class__.__name__ == "AudienceTrackingSubscriptionExpired"

    def test_expire_already_inactive(self):
        """Test expiring already inactive subscription."""
        tracking = self._create_test_tracking()
        tracking.tracking_id = TrackingId(1)
        tracking.is_active = False
        
        tracking.expire()
        
        # Should not raise event if already inactive
        assert len(tracking.domain_events) == 0

    def test_enable_auto_renew(self):
        """Test enabling auto-renewal."""
        tracking = self._create_test_tracking()
        
        tracking.enable_auto_renew()
        
        assert tracking.auto_renew is True

    def test_disable_auto_renew(self):
        """Test disabling auto-renewal."""
        tracking = self._create_test_tracking()
        tracking.auto_renew = True
        
        tracking.disable_auto_renew()
        
        assert tracking.auto_renew is False

    def test_is_expired(self):
        """Test is_expired check."""
        tracking = self._create_test_tracking()
        
        # Not expired
        tracking.expires_at = datetime.utcnow() + timedelta(days=1)
        assert not tracking.is_expired()
        
        # Expired
        tracking.expires_at = datetime.utcnow() - timedelta(days=1)
        assert tracking.is_expired()

    def test_days_remaining(self):
        """Test days_remaining calculation."""
        tracking = self._create_test_tracking()
        
        # 5 days remaining
        tracking.expires_at = datetime.utcnow() + timedelta(days=5, hours=12)
        assert tracking.days_remaining() == 5
        
        # Expired
        tracking.expires_at = datetime.utcnow() - timedelta(days=1)
        assert tracking.days_remaining() == 0

    def test_str_representation(self):
        """Test string representation."""
        tracking = self._create_test_tracking()
        
        result = str(tracking)
        
        assert "AudienceTracking" in result
        assert "testuser" in result
        assert "active" in result

    def _create_test_tracking(self) -> AudienceTracking:
        """Helper to create test tracking."""
        price = TrackingPrice.for_stars()
        return AudienceTracking.create(
            user_id=123,
            target_username="testuser",
            target_user_id="456",
            price=price
        )

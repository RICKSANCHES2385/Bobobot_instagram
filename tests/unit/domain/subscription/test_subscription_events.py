"""Tests for Subscription Events."""
from src.domain.subscription.events.subscription_events import (
    SubscriptionCreated,
    SubscriptionRenewed,
    SubscriptionCancelled,
    SubscriptionExpired
)


def test_subscription_created_event():
    """Test SubscriptionCreated event creation."""
    event = SubscriptionCreated(
        subscription_id=1,
        user_id=123,
        subscription_type="BASIC",
        end_date="2026-02-01T00:00:00"
    )
    
    assert event.subscription_id == 1
    assert event.user_id == 123
    assert event.subscription_type == "BASIC"
    assert event.end_date == "2026-02-01T00:00:00"
    assert event.event_id is not None
    assert event.occurred_at is not None


def test_subscription_renewed_event():
    """Test SubscriptionRenewed event creation."""
    event = SubscriptionRenewed(
        subscription_id=1,
        user_id=123,
        old_end_date="2026-02-01T00:00:00",
        new_end_date="2026-03-01T00:00:00",
        days_added=30
    )
    
    assert event.subscription_id == 1
    assert event.user_id == 123
    assert event.old_end_date == "2026-02-01T00:00:00"
    assert event.new_end_date == "2026-03-01T00:00:00"
    assert event.days_added == 30


def test_subscription_cancelled_event():
    """Test SubscriptionCancelled event creation."""
    event = SubscriptionCancelled(
        subscription_id=1,
        user_id=123,
        cancelled_at="2026-01-15T00:00:00"
    )
    
    assert event.subscription_id == 1
    assert event.user_id == 123
    assert event.cancelled_at == "2026-01-15T00:00:00"


def test_subscription_expired_event():
    """Test SubscriptionExpired event creation."""
    event = SubscriptionExpired(
        subscription_id=1,
        user_id=123,
        expired_at="2026-02-01T00:00:00"
    )
    
    assert event.subscription_id == 1
    assert event.user_id == 123
    assert event.expired_at == "2026-02-01T00:00:00"

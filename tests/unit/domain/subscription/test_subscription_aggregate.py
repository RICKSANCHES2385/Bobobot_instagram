"""Tests for Subscription Aggregate."""
import pytest
from datetime import datetime, timedelta
from src.domain.subscription.aggregates.subscription import Subscription
from src.domain.subscription.value_objects.subscription_id import SubscriptionId
from src.domain.subscription.value_objects.subscription_type import SubscriptionType
from src.domain.subscription.value_objects.subscription_status import SubscriptionStatus
from src.domain.subscription.value_objects.subscription_period import SubscriptionPeriod
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.shared.value_objects.money import Money
from src.domain.subscription.events.subscription_events import (
    SubscriptionCreated,
    SubscriptionRenewed,
    SubscriptionCancelled,
    SubscriptionExpired
)


def test_subscription_create():
    """Test subscription creation."""
    user_id = UserId(value=123)
    sub_type = SubscriptionType.basic()
    period = SubscriptionPeriod.from_days(days=30)
    
    subscription = Subscription.create(
        user_id=user_id,
        subscription_type=sub_type,
        period=period,
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    assert subscription.user_id == user_id
    assert subscription.type == sub_type
    assert subscription.status.is_active()
    assert subscription.period == period


def test_subscription_renew():
    """Test subscription renewal."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    old_end_date = subscription.period.end_date
    subscription.renew(days=30)
    
    assert subscription.period.end_date > old_end_date
    assert subscription.status.is_active()


def test_subscription_renew_inactive_raises():
    """Test renewing inactive subscription raises error."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.cancel()
    
    with pytest.raises(ValueError, match="Cannot renew inactive subscription"):
        subscription.renew(days=30)


def test_subscription_cancel():
    """Test subscription cancellation."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.cancel()
    
    assert not subscription.status.is_active()


def test_subscription_cancel_inactive_raises():
    """Test cancelling inactive subscription raises error."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.cancel()
    
    with pytest.raises(ValueError, match="Cannot cancel inactive subscription"):
        subscription.cancel()


def test_subscription_check_expiration():
    """Test subscription expiration check."""
    # Create expired subscription
    past_start = datetime.utcnow() - timedelta(days=30)
    past_end = datetime.utcnow() - timedelta(days=1)
    period = SubscriptionPeriod(start_date=past_start, end_date=past_end)
    
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=period,
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.check_expiration()
    
    assert not subscription.status.is_active()


def test_subscription_is_active():
    """Test is_active method."""
    # Active subscription
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    assert subscription.is_active()
    
    # Cancelled subscription
    subscription.cancel()
    assert not subscription.is_active()


def test_subscription_days_remaining():
    """Test days_remaining method."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    assert subscription.days_remaining() >= 29  # Allow for timing
    
    # Cancelled subscription
    subscription.cancel()
    assert subscription.days_remaining() == 0


def test_subscription_create_emits_event():
    """Test subscription creation emits event."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    events = subscription.domain_events
    assert len(events) == 1
    assert isinstance(events[0], SubscriptionCreated)
    assert events[0].user_id == 123


def test_subscription_renew_emits_event():
    """Test subscription renewal emits event."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.clear_domain_events()
    subscription.renew(days=30)
    
    events = subscription.domain_events
    assert len(events) == 1
    assert isinstance(events[0], SubscriptionRenewed)
    assert events[0].days_added == 30


def test_subscription_cancel_emits_event():
    """Test subscription cancellation emits event."""
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=SubscriptionPeriod.from_days(days=30),
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.clear_domain_events()
    subscription.cancel()
    
    events = subscription.domain_events
    assert len(events) == 1
    assert isinstance(events[0], SubscriptionCancelled)


def test_subscription_expire_emits_event():
    """Test subscription expiration emits event."""
    # Create expired subscription
    past_start = datetime.utcnow() - timedelta(days=30)
    past_end = datetime.utcnow() - timedelta(days=1)
    period = SubscriptionPeriod(start_date=past_start, end_date=past_end)
    
    subscription = Subscription.create(
        user_id=UserId(value=123),
        subscription_type=SubscriptionType.basic(),
        period=period,
        price=Money(amount=100.0, currency="RUB"),
        auto_renew=False
    )
    
    subscription.clear_domain_events()
    subscription.check_expiration()
    
    events = subscription.domain_events
    assert len(events) == 1
    assert isinstance(events[0], SubscriptionExpired)

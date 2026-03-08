"""Tests for SubscriptionPeriod Value Object."""
import pytest
from datetime import datetime, timedelta
from src.domain.subscription.value_objects.subscription_period import SubscriptionPeriod


def test_subscription_period_creation():
    """Test subscription period creation."""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    period = SubscriptionPeriod(start_date=start, end_date=end)
    
    assert period.start_date == start
    assert period.end_date == end


def test_subscription_period_validates_dates():
    """Test subscription period validates start before end."""
    start = datetime(2026, 1, 31)
    end = datetime(2026, 1, 1)
    
    with pytest.raises(ValueError, match="Start date must be before end date"):
        SubscriptionPeriod(start_date=start, end_date=end)


def test_subscription_period_from_days():
    """Test creating period from days."""
    start = datetime(2026, 1, 1)
    period = SubscriptionPeriod.from_days(days=30, start_date=start)
    
    assert period.start_date == start
    assert period.end_date == start + timedelta(days=30)


def test_subscription_period_from_days_validates_positive():
    """Test from_days validates positive days."""
    with pytest.raises(ValueError, match="Days must be positive"):
        SubscriptionPeriod.from_days(days=0)
    
    with pytest.raises(ValueError, match="Days must be positive"):
        SubscriptionPeriod.from_days(days=-1)


def test_subscription_period_is_expired():
    """Test is_expired method."""
    # Expired period
    past_start = datetime.utcnow() - timedelta(days=30)
    past_end = datetime.utcnow() - timedelta(days=1)
    expired_period = SubscriptionPeriod(start_date=past_start, end_date=past_end)
    assert expired_period.is_expired()
    
    # Active period
    future_start = datetime.utcnow()
    future_end = datetime.utcnow() + timedelta(days=30)
    active_period = SubscriptionPeriod(start_date=future_start, end_date=future_end)
    assert not active_period.is_expired()


def test_subscription_period_days_remaining():
    """Test days_remaining method."""
    # Expired period
    past_start = datetime.utcnow() - timedelta(days=30)
    past_end = datetime.utcnow() - timedelta(days=1)
    expired_period = SubscriptionPeriod(start_date=past_start, end_date=past_end)
    assert expired_period.days_remaining() == 0
    
    # Active period
    start = datetime.utcnow()
    end = datetime.utcnow() + timedelta(days=30)
    active_period = SubscriptionPeriod(start_date=start, end_date=end)
    assert active_period.days_remaining() >= 29  # Allow for timing


def test_subscription_period_extend():
    """Test extend method."""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    period = SubscriptionPeriod(start_date=start, end_date=end)
    
    extended = period.extend(days=30)
    
    assert extended.start_date == start
    assert extended.end_date == end + timedelta(days=30)
    
    # Original period unchanged
    assert period.end_date == end


def test_subscription_period_extend_validates_positive():
    """Test extend validates positive days."""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    period = SubscriptionPeriod(start_date=start, end_date=end)
    
    with pytest.raises(ValueError, match="Days must be positive"):
        period.extend(days=0)
    
    with pytest.raises(ValueError, match="Days must be positive"):
        period.extend(days=-1)

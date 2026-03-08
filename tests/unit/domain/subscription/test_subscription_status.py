"""Tests for SubscriptionStatus Value Object."""
import pytest
from src.domain.subscription.value_objects.subscription_status import (
    SubscriptionStatus,
    SubscriptionStatusEnum
)


def test_subscription_status_creation():
    """Test subscription status creation."""
    status = SubscriptionStatus(status=SubscriptionStatusEnum.ACTIVE)
    assert status.status == SubscriptionStatusEnum.ACTIVE


def test_subscription_status_active():
    """Test ACTIVE status factory."""
    status = SubscriptionStatus.active()
    assert status.status == SubscriptionStatusEnum.ACTIVE
    assert status.is_active()


def test_subscription_status_expired():
    """Test EXPIRED status factory."""
    status = SubscriptionStatus.expired()
    assert status.status == SubscriptionStatusEnum.EXPIRED
    assert not status.is_active()


def test_subscription_status_cancelled():
    """Test CANCELLED status factory."""
    status = SubscriptionStatus.cancelled()
    assert status.status == SubscriptionStatusEnum.CANCELLED
    assert not status.is_active()


def test_subscription_status_is_active():
    """Test is_active method."""
    assert SubscriptionStatus.active().is_active()
    assert not SubscriptionStatus.expired().is_active()
    assert not SubscriptionStatus.cancelled().is_active()


def test_subscription_status_validates_status():
    """Test subscription status validation."""
    with pytest.raises(ValueError, match="Invalid subscription status"):
        SubscriptionStatus(status="INVALID")  # type: ignore

"""Tests for SubscriptionType Value Object."""
import pytest
from src.domain.subscription.value_objects.subscription_type import (
    SubscriptionType,
    SubscriptionTypeEnum
)


def test_subscription_type_creation():
    """Test subscription type creation."""
    sub_type = SubscriptionType(type=SubscriptionTypeEnum.BASIC)
    assert sub_type.type == SubscriptionTypeEnum.BASIC


def test_subscription_type_free():
    """Test FREE subscription type factory."""
    sub_type = SubscriptionType.free()
    assert sub_type.type == SubscriptionTypeEnum.FREE
    assert sub_type.is_free()


def test_subscription_type_basic():
    """Test BASIC subscription type factory."""
    sub_type = SubscriptionType.basic()
    assert sub_type.type == SubscriptionTypeEnum.BASIC
    assert sub_type.is_paid()


def test_subscription_type_premium():
    """Test PREMIUM subscription type factory."""
    sub_type = SubscriptionType.premium()
    assert sub_type.type == SubscriptionTypeEnum.PREMIUM
    assert sub_type.is_paid()


def test_subscription_type_is_free():
    """Test is_free method."""
    assert SubscriptionType.free().is_free()
    assert not SubscriptionType.basic().is_free()
    assert not SubscriptionType.premium().is_free()


def test_subscription_type_is_paid():
    """Test is_paid method."""
    assert not SubscriptionType.free().is_paid()
    assert SubscriptionType.basic().is_paid()
    assert SubscriptionType.premium().is_paid()


def test_subscription_type_validates_type():
    """Test subscription type validation."""
    with pytest.raises(ValueError, match="Invalid subscription type"):
        SubscriptionType(type="INVALID")  # type: ignore

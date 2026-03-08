"""Tests for SubscriptionId Value Object."""
import pytest
from src.domain.subscription.value_objects.subscription_id import SubscriptionId


def test_subscription_id_creation():
    """Test subscription ID creation."""
    sub_id = SubscriptionId(value=123)
    assert sub_id.value == 123


def test_subscription_id_equality():
    """Test subscription ID equality."""
    sub_id1 = SubscriptionId(value=123)
    sub_id2 = SubscriptionId(value=123)
    sub_id3 = SubscriptionId(value=456)
    
    assert sub_id1 == sub_id2
    assert sub_id1 != sub_id3


def test_subscription_id_hash():
    """Test subscription ID can be hashed."""
    sub_id1 = SubscriptionId(value=123)
    sub_id2 = SubscriptionId(value=123)
    
    assert hash(sub_id1) == hash(sub_id2)
    assert len({sub_id1, sub_id2}) == 1

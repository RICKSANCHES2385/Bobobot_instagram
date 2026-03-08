"""Tests for Subscription Exceptions."""
import pytest
from src.domain.subscription.exceptions import (
    SubscriptionNotFoundException,
    SubscriptionAlreadyExistsException,
    InvalidSubscriptionOperationException
)


def test_subscription_not_found_exception():
    """Test SubscriptionNotFoundException."""
    exc = SubscriptionNotFoundException(identifier="sub_123")
    
    assert "Subscription not found: sub_123" in str(exc)
    assert exc.code == "SUBSCRIPTION_NOT_FOUND"


def test_subscription_already_exists_exception():
    """Test SubscriptionAlreadyExistsException."""
    exc = SubscriptionAlreadyExistsException(user_id=123)
    
    assert "Active subscription already exists for user 123" in str(exc)
    assert exc.code == "SUBSCRIPTION_ALREADY_EXISTS"


def test_invalid_subscription_operation_exception():
    """Test InvalidSubscriptionOperationException."""
    exc = InvalidSubscriptionOperationException(message="Cannot renew expired subscription")
    
    assert "Cannot renew expired subscription" in str(exc)
    assert exc.code == "INVALID_SUBSCRIPTION_OPERATION"

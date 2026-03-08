"""Tests for UserId."""
import pytest
from src.domain.user_management.value_objects.user_id import UserId


def test_user_id_creation():
    """UserId should be created with int value."""
    user_id = UserId(value=123)
    
    assert user_id.value == 123
    assert int(user_id) == 123


def test_user_id_equality():
    """UserIds with same value should be equal."""
    user_id1 = UserId(value=123)
    user_id2 = UserId(value=123)
    user_id3 = UserId(value=456)
    
    assert user_id1 == user_id2
    assert user_id1 != user_id3


def test_user_id_hash():
    """UserId should be hashable."""
    user_id1 = UserId(value=123)
    user_id2 = UserId(value=123)
    
    assert hash(user_id1) == hash(user_id2)
    assert {user_id1, user_id2} == {user_id1}

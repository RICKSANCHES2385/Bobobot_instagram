"""Tests for Username."""
import pytest
from src.domain.user_management.value_objects.username import Username


def test_username_creation():
    """Username should be created with valid string."""
    username = Username(value="john_doe")
    
    assert username.value == "john_doe"


def test_username_validates_empty():
    """Username should not be empty."""
    with pytest.raises(ValueError, match="Username cannot be empty"):
        Username(value="")


def test_username_validates_length():
    """Username should not exceed 32 characters."""
    with pytest.raises(ValueError, match="Username too long"):
        Username(value="a" * 33)


def test_username_validates_format():
    """Username should only contain letters, numbers and underscores."""
    # Valid usernames
    Username(value="john_doe")
    Username(value="user123")
    Username(value="test_user_123")
    
    # Invalid usernames
    with pytest.raises(ValueError, match="Username can only contain"):
        Username(value="john-doe")  # hyphen not allowed
    
    with pytest.raises(ValueError, match="Username can only contain"):
        Username(value="john.doe")  # dot not allowed
    
    with pytest.raises(ValueError, match="Username can only contain"):
        Username(value="john doe")  # space not allowed

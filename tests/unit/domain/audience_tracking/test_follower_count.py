"""Tests for FollowerCount value object."""

import pytest

from src.domain.audience_tracking.value_objects.follower_count import FollowerCount


class TestFollowerCount:
    """Test FollowerCount value object."""

    def test_create_valid_count(self):
        """Test creating valid follower count."""
        count = FollowerCount(value=1000)
        
        assert count.value == 1000

    def test_create_zero_count(self):
        """Test creating zero follower count."""
        count = FollowerCount(value=0)
        
        assert count.value == 0

    def test_negative_count(self):
        """Test creating negative follower count."""
        with pytest.raises(ValueError, match="Follower count cannot be negative"):
            FollowerCount(value=-1)

    def test_invalid_type(self):
        """Test creating follower count with invalid type."""
        with pytest.raises(ValueError, match="Follower count must be an integer"):
            FollowerCount(value="1000")  # type: ignore

    def test_exceeds_limit_default(self):
        """Test exceeds_limit with default limit."""
        count_below = FollowerCount(value=50000)
        count_at = FollowerCount(value=100000)
        count_above = FollowerCount(value=100001)
        
        assert not count_below.exceeds_limit()
        assert not count_at.exceeds_limit()
        assert count_above.exceeds_limit()

    def test_exceeds_limit_custom(self):
        """Test exceeds_limit with custom limit."""
        count = FollowerCount(value=5000)
        
        assert not count.exceeds_limit(limit=10000)
        assert count.exceeds_limit(limit=1000)

    def test_str_representation(self):
        """Test string representation."""
        count = FollowerCount(value=1234567)
        
        assert str(count) == "1,234,567"

    def test_immutability(self):
        """Test that count is immutable."""
        count = FollowerCount(value=1000)
        
        with pytest.raises(Exception):  # FrozenInstanceError
            count.value = 2000  # type: ignore

    def test_equality(self):
        """Test count equality."""
        count1 = FollowerCount(value=1000)
        count2 = FollowerCount(value=1000)
        count3 = FollowerCount(value=2000)
        
        assert count1 == count2
        assert count1 != count3

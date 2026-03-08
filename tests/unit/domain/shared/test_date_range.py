"""Tests for DateRange."""
import pytest
from datetime import datetime, timedelta
from src.domain.shared.value_objects.date_range import DateRange


def test_date_range_creation():
    """DateRange should be created with start and end dates."""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    
    date_range = DateRange(start_date=start, end_date=end)
    
    assert date_range.start_date == start
    assert date_range.end_date == end


def test_date_range_validates_order():
    """DateRange should validate that start is before end."""
    start = datetime(2026, 1, 31)
    end = datetime(2026, 1, 1)
    
    with pytest.raises(ValueError, match="Start date must be before or equal to end date"):
        DateRange(start_date=start, end_date=end)


def test_date_range_contains():
    """DateRange should check if date is within range."""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    date_range = DateRange(start_date=start, end_date=end)
    
    assert date_range.contains(datetime(2026, 1, 15))
    assert date_range.contains(datetime(2026, 1, 1))  # Start boundary
    assert date_range.contains(datetime(2026, 1, 31))  # End boundary
    assert not date_range.contains(datetime(2025, 12, 31))
    assert not date_range.contains(datetime(2026, 2, 1))


def test_date_range_overlaps():
    """DateRange should check if it overlaps with another range."""
    range1 = DateRange(
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 15)
    )
    range2 = DateRange(
        start_date=datetime(2026, 1, 10),
        end_date=datetime(2026, 1, 20)
    )
    range3 = DateRange(
        start_date=datetime(2026, 1, 20),
        end_date=datetime(2026, 1, 31)
    )
    
    assert range1.overlaps(range2)
    assert range2.overlaps(range1)
    assert not range1.overlaps(range3)


def test_date_range_duration():
    """DateRange should calculate duration."""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    date_range = DateRange(start_date=start, end_date=end)
    
    duration = date_range.duration()
    
    assert duration == timedelta(days=30)


def test_date_range_string_representation():
    """DateRange should have string representation."""
    start = datetime(2026, 1, 1, 12, 0, 0)
    end = datetime(2026, 1, 31, 12, 0, 0)
    date_range = DateRange(start_date=start, end_date=end)
    
    assert "2026-01-01" in str(date_range)
    assert "2026-01-31" in str(date_range)

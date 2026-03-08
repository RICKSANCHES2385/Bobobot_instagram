"""DateRange Value Object."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from .base import BaseValueObject


@dataclass(frozen=True)
class DateRange(BaseValueObject):
    """Date range value object."""
    
    start_date: datetime
    end_date: datetime
    
    def _validate(self) -> None:
        """Validate date range."""
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")
    
    def contains(self, date: datetime) -> bool:
        """Check if date is within range."""
        return self.start_date <= date <= self.end_date
    
    def overlaps(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another."""
        return self.start_date <= other.end_date and other.start_date <= self.end_date
    
    def duration(self) -> timedelta:
        """Get duration of the range."""
        return self.end_date - self.start_date
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.start_date.isoformat()} to {self.end_date.isoformat()}"

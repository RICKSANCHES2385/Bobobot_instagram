"""Subscription Period Value Object."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class SubscriptionPeriod(BaseValueObject):
    """Subscription period with start and end dates."""
    
    start_date: datetime
    end_date: datetime
    
    def _validate(self) -> None:
        """Validate subscription period."""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
    
    @classmethod
    def from_days(cls, days: int, start_date: datetime | None = None) -> 'SubscriptionPeriod':
        """Create period from number of days.
        
        Args:
            days: Number of days for the period.
            start_date: Start date (defaults to now).
            
        Returns:
            SubscriptionPeriod instance.
            
        Raises:
            ValueError: If days is not positive.
        """
        if days <= 0:
            raise ValueError("Days must be positive")
        
        start = start_date or datetime.utcnow()
        end = start + timedelta(days=days)
        return cls(start_date=start, end_date=end)
    
    def is_expired(self) -> bool:
        """Check if period is expired."""
        return datetime.utcnow() > self.end_date
    
    def days_remaining(self) -> int:
        """Get remaining days."""
        if self.is_expired():
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def extend(self, days: int) -> 'SubscriptionPeriod':
        """Extend period by days.
        
        Args:
            days: Number of days to extend.
            
        Returns:
            New SubscriptionPeriod with extended end date.
            
        Raises:
            ValueError: If days is not positive.
        """
        if days <= 0:
            raise ValueError("Days must be positive")
        
        new_end = self.end_date + timedelta(days=days)
        return SubscriptionPeriod(start_date=self.start_date, end_date=new_end)

"""Subscription DTOs."""
from dataclasses import dataclass


@dataclass
class CreateSubscriptionCommand:
    """Create subscription command."""
    user_id: int
    subscription_type: str
    days: int
    price: float = 100.0  # Default price


@dataclass
class RenewSubscriptionCommand:
    """Renew subscription command."""
    user_id: int
    days: int


@dataclass
class CancelSubscriptionCommand:
    """Cancel subscription command."""
    user_id: int


@dataclass
class SubscriptionDTO:
    """Subscription data transfer object."""
    id: int
    user_id: int
    subscription_type: str
    status: str
    start_date: str
    end_date: str
    days_remaining: int
    is_active: bool
    created_at: str
    updated_at: str

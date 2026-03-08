"""Subscription Status Value Object."""
from dataclasses import dataclass
from enum import Enum
from src.domain.shared.value_objects.base import BaseValueObject


class SubscriptionStatusEnum(str, Enum):
    """Subscription status enum."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class SubscriptionStatus(BaseValueObject):
    """Subscription status."""
    
    status: SubscriptionStatusEnum
    
    def _validate(self) -> None:
        """Validate subscription status."""
        if not isinstance(self.status, SubscriptionStatusEnum):
            raise ValueError(f"Invalid subscription status: {self.status}")
    
    @classmethod
    def active(cls) -> 'SubscriptionStatus':
        """Get ACTIVE status."""
        return cls(status=SubscriptionStatusEnum.ACTIVE)
    
    @classmethod
    def expired(cls) -> 'SubscriptionStatus':
        """Get EXPIRED status."""
        return cls(status=SubscriptionStatusEnum.EXPIRED)
    
    @classmethod
    def cancelled(cls) -> 'SubscriptionStatus':
        """Get CANCELLED status."""
        return cls(status=SubscriptionStatusEnum.CANCELLED)
    
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == SubscriptionStatusEnum.ACTIVE

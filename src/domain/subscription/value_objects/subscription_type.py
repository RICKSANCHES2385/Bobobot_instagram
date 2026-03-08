"""Subscription Type Value Object."""
from dataclasses import dataclass
from enum import Enum
from src.domain.shared.value_objects.base import BaseValueObject


class SubscriptionTypeEnum(str, Enum):
    """Subscription type enum."""
    FREE = "FREE"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"


@dataclass(frozen=True)
class SubscriptionType(BaseValueObject):
    """Subscription type."""
    
    type: SubscriptionTypeEnum
    
    def _validate(self) -> None:
        """Validate subscription type."""
        if not isinstance(self.type, SubscriptionTypeEnum):
            raise ValueError(f"Invalid subscription type: {self.type}")
    
    @classmethod
    def free(cls) -> 'SubscriptionType':
        """Get FREE subscription type."""
        return cls(type=SubscriptionTypeEnum.FREE)
    
    @classmethod
    def basic(cls) -> 'SubscriptionType':
        """Get BASIC subscription type."""
        return cls(type=SubscriptionTypeEnum.BASIC)
    
    @classmethod
    def premium(cls) -> 'SubscriptionType':
        """Get PREMIUM subscription type."""
        return cls(type=SubscriptionTypeEnum.PREMIUM)
    
    def is_free(self) -> bool:
        """Check if subscription is free."""
        return self.type == SubscriptionTypeEnum.FREE
    
    def is_paid(self) -> bool:
        """Check if subscription is paid."""
        return self.type in (SubscriptionTypeEnum.BASIC, SubscriptionTypeEnum.PREMIUM)

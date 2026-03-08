"""Subscription Status Value Object."""

from dataclasses import dataclass
from enum import Enum


class SubscriptionStatusEnum(str, Enum):
    """Subscription status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"


@dataclass(frozen=True)
class SubscriptionStatus:
    """Subscription status value object."""

    value: SubscriptionStatusEnum

    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.value in (SubscriptionStatusEnum.ACTIVE, SubscriptionStatusEnum.TRIAL)

    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        return self.value == SubscriptionStatusEnum.EXPIRED

    def is_cancelled(self) -> bool:
        """Check if subscription is cancelled."""
        return self.value == SubscriptionStatusEnum.CANCELLED

    def is_trial(self) -> bool:
        """Check if subscription is trial."""
        return self.value == SubscriptionStatusEnum.TRIAL

    def __str__(self) -> str:
        """String representation."""
        return self.value.value

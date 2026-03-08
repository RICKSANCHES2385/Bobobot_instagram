"""Subscription Aggregate Root."""
from dataclasses import dataclass
from datetime import datetime
from src.domain.shared.entities.base import AggregateRoot
from src.domain.shared.value_objects.money import Money
from ..value_objects.subscription_id import SubscriptionId
from ..value_objects.subscription_type import SubscriptionType
from ..value_objects.subscription_status import SubscriptionStatus
from ..value_objects.subscription_period import SubscriptionPeriod
from src.domain.user_management.value_objects.user_id import UserId
from ..events.subscription_events import (
    SubscriptionCreated,
    SubscriptionRenewed,
    SubscriptionCancelled,
    SubscriptionExpired
)


@dataclass(eq=False)
class Subscription(AggregateRoot):
    """Subscription aggregate root.
    
    Represents a user subscription with type, status, and period.
    """
    
    user_id: UserId = None  # type: ignore
    type: SubscriptionType = None  # type: ignore
    status: SubscriptionStatus = None  # type: ignore
    period: SubscriptionPeriod = None  # type: ignore
    price: Money = None  # type: ignore
    auto_renew: bool = False
    
    @staticmethod
    def create(
        user_id: UserId,
        subscription_type: SubscriptionType,
        period: SubscriptionPeriod,
        price: Money,
        auto_renew: bool = False
    ) -> 'Subscription':
        """Create a new subscription.
        
        Args:
            user_id: User ID.
            subscription_type: Subscription type.
            period: Subscription period.
            price: Subscription price.
            auto_renew: Auto-renewal flag.
            
        Returns:
            New Subscription instance.
        """
        from uuid import uuid4
        subscription_id = SubscriptionId(uuid4())
        
        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            type=subscription_type,
            status=SubscriptionStatus.active(),
            period=period,
            price=price,
            auto_renew=auto_renew
        )
        
        subscription.add_domain_event(
            SubscriptionCreated(
                subscription_id=subscription_id.value,
                user_id=user_id.value,
                subscription_type=subscription_type.type.value,
                end_date=period.end_date.isoformat()
            )
        )
        
        return subscription
    
    def renew(self, days: int) -> None:
        """Renew subscription by extending period.
        
        Args:
            days: Number of days to extend.
            
        Raises:
            ValueError: If subscription is not active.
        """
        if not self.status.is_active():
            raise ValueError("Cannot renew inactive subscription")
        
        old_end_date = self.period.end_date
        object.__setattr__(self, 'period', self.period.extend(days))
        self._touch()
        
        self.add_domain_event(
            SubscriptionRenewed(
                subscription_id=self.id.value,
                user_id=self.user_id.value,
                old_end_date=old_end_date.isoformat(),
                new_end_date=self.period.end_date.isoformat(),
                days_added=days
            )
        )
    
    def cancel(self) -> None:
        """Cancel subscription.
        
        Raises:
            ValueError: If subscription is not active.
        """
        if not self.status.is_active():
            raise ValueError("Cannot cancel inactive subscription")
        
        object.__setattr__(self, 'status', SubscriptionStatus.cancelled())
        self._touch()
        
        self.add_domain_event(
            SubscriptionCancelled(
                subscription_id=self.id.value,
                user_id=self.user_id.value,
                cancelled_at=datetime.utcnow().isoformat()
            )
        )
    
    def check_expiration(self) -> None:
        """Check and update expiration status."""
        if self.status.is_active() and self.period.is_expired():
            object.__setattr__(self, 'status', SubscriptionStatus.expired())
            self._touch()
            
            self.add_domain_event(
                SubscriptionExpired(
                    subscription_id=self.id.value,
                    user_id=self.user_id.value,
                    expired_at=self.period.end_date.isoformat()
                )
            )
    
    def is_active(self) -> bool:
        """Check if subscription is active and not expired."""
        self.check_expiration()
        return self.status.is_active()
    
    def days_remaining(self) -> int:
        """Get remaining days."""
        if not self.is_active():
            return 0
        return self.period.days_remaining()

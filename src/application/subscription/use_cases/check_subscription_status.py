"""Check Subscription Status Use Case."""
from dataclasses import dataclass
from ...shared.use_case import UseCase
from ....domain.subscription.repositories.subscription_repository import SubscriptionRepository
from ....domain.user_management.value_objects.user_id import UserId


@dataclass
class SubscriptionStatusDTO:
    """Subscription status DTO."""
    has_active_subscription: bool
    days_remaining: int
    subscription_type: str | None


class CheckSubscriptionStatusUseCase(UseCase[int, SubscriptionStatusDTO]):
    """Check if user has active subscription."""
    
    def __init__(self, subscription_repository: SubscriptionRepository):
        """Initialize use case.
        
        Args:
            subscription_repository: Subscription repository.
        """
        self.subscription_repository = subscription_repository
    
    async def execute(self, user_id: int) -> SubscriptionStatusDTO:
        """Execute use case.
        
        Args:
            user_id: User ID.
            
        Returns:
            Subscription status DTO.
        """
        user_id_vo = UserId(value=user_id)
        subscription = await self.subscription_repository.get_active_by_user_id(user_id_vo)
        
        if subscription is None:
            return SubscriptionStatusDTO(
                has_active_subscription=False,
                days_remaining=0,
                subscription_type=None
            )
        
        return SubscriptionStatusDTO(
            has_active_subscription=subscription.is_active(),
            days_remaining=subscription.days_remaining(),
            subscription_type=subscription.type.type.value
        )

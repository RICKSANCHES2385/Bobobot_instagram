"""Get Subscription Use Case."""
from ..dtos import SubscriptionDTO
from ...shared.use_case import UseCase
from ....domain.subscription.repositories.subscription_repository import SubscriptionRepository
from ....domain.subscription.exceptions import SubscriptionNotFoundException
from ....domain.user_management.value_objects.user_id import UserId


class GetSubscriptionUseCase(UseCase[int, SubscriptionDTO]):
    """Get active subscription for user."""
    
    def __init__(self, subscription_repository: SubscriptionRepository):
        """Initialize use case.
        
        Args:
            subscription_repository: Subscription repository.
        """
        self.subscription_repository = subscription_repository
    
    async def execute(self, user_id: int) -> SubscriptionDTO:
        """Execute use case.
        
        Args:
            user_id: User ID.
            
        Returns:
            Subscription DTO.
            
        Raises:
            SubscriptionNotFoundException: If subscription not found.
        """
        user_id_vo = UserId(value=user_id)
        subscription = await self.subscription_repository.get_active_by_user_id(user_id_vo)
        
        if subscription is None:
            raise SubscriptionNotFoundException(identifier=f"user_id={user_id}")
        
        return SubscriptionDTO(
            id=subscription.id.value,
            user_id=subscription.user_id.value,
            subscription_type=subscription.type.type.value,
            status=subscription.status.status.value,
            start_date=subscription.period.start_date.isoformat(),
            end_date=subscription.period.end_date.isoformat(),
            days_remaining=subscription.days_remaining(),
            is_active=subscription.is_active(),
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat()
        )

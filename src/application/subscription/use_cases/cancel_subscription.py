"""Cancel Subscription Use Case."""
from ..dtos import CancelSubscriptionCommand, SubscriptionDTO
from ...shared.use_case import UseCase
from ....domain.subscription.repositories.subscription_repository import SubscriptionRepository
from ....domain.subscription.exceptions import SubscriptionNotFoundException
from ....domain.user_management.value_objects.user_id import UserId


class CancelSubscriptionUseCase(UseCase[CancelSubscriptionCommand, SubscriptionDTO]):
    """Cancel an existing subscription."""
    
    def __init__(self, subscription_repository: SubscriptionRepository):
        """Initialize use case.
        
        Args:
            subscription_repository: Subscription repository.
        """
        self.subscription_repository = subscription_repository
    
    async def execute(self, command: CancelSubscriptionCommand) -> SubscriptionDTO:
        """Execute use case.
        
        Args:
            command: Cancel subscription command.
            
        Returns:
            Subscription DTO.
            
        Raises:
            SubscriptionNotFoundException: If subscription not found.
        """
        user_id = UserId(value=command.user_id)
        
        # Get active subscription
        subscription = await self.subscription_repository.get_active_by_user_id(user_id)
        if subscription is None:
            raise SubscriptionNotFoundException(identifier=f"user_id={command.user_id}")
        
        # Cancel subscription
        subscription.cancel()
        
        # Save subscription
        await self.subscription_repository.save(subscription)
        
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

"""Create Subscription Use Case."""
from ..dtos import CreateSubscriptionCommand, SubscriptionDTO
from ...shared.use_case import UseCase
from ....domain.subscription.aggregates.subscription import Subscription
from ....domain.subscription.value_objects.subscription_id import SubscriptionId
from ....domain.subscription.value_objects.subscription_type import (
    SubscriptionType,
    SubscriptionTypeEnum
)
from ....domain.subscription.value_objects.subscription_period import SubscriptionPeriod
from ....domain.subscription.repositories.subscription_repository import SubscriptionRepository
from ....domain.subscription.exceptions import SubscriptionAlreadyExistsException
from ....domain.user_management.value_objects.user_id import UserId
from ....domain.shared.value_objects.money import Money


class CreateSubscriptionUseCase(UseCase[CreateSubscriptionCommand, SubscriptionDTO]):
    """Create a new subscription."""
    
    def __init__(self, subscription_repository: SubscriptionRepository):
        """Initialize use case.
        
        Args:
            subscription_repository: Subscription repository.
        """
        self.subscription_repository = subscription_repository
    
    async def execute(self, command: CreateSubscriptionCommand) -> SubscriptionDTO:
        """Execute use case.
        
        Args:
            command: Create subscription command.
            
        Returns:
            Subscription DTO.
            
        Raises:
            SubscriptionAlreadyExistsException: If active subscription exists.
        """
        user_id = UserId(value=command.user_id)
        
        # Check if active subscription exists
        existing = await self.subscription_repository.get_active_by_user_id(user_id)
        if existing:
            raise SubscriptionAlreadyExistsException(user_id=command.user_id)
        
        # Create subscription
        subscription_type = SubscriptionType(type=SubscriptionTypeEnum(command.subscription_type))
        period = SubscriptionPeriod.from_days(days=command.days)
        price = Money(amount=command.price, currency="RUB")
        
        subscription = Subscription.create(
            user_id=user_id,
            subscription_type=subscription_type,
            period=period,
            price=price,
            auto_renew=False
        )
        
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

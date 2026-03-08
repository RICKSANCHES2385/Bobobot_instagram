"""Renew Audience Tracking Use Case."""

from src.application.shared.use_case import UseCase
from src.application.audience_tracking.dtos import RenewTrackingDTO, AudienceTrackingDTO
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId
from src.domain.audience_tracking.value_objects.tracking_price import TrackingPrice
from src.domain.audience_tracking.exceptions import TrackingNotFoundException
from src.domain.audience_tracking.aggregates.audience_tracking import AudienceTracking
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RenewAudienceTrackingUseCase(UseCase[RenewTrackingDTO, AudienceTrackingDTO]):
    """Use case for renewing audience tracking subscription."""

    def __init__(self, tracking_repository: AudienceTrackingRepository):
        """Initialize use case.
        
        Args:
            tracking_repository: Audience tracking repository
        """
        self.tracking_repository = tracking_repository

    async def execute(self, dto: RenewTrackingDTO) -> AudienceTrackingDTO:
        """Execute use case.
        
        Args:
            dto: Renew tracking DTO
            
        Returns:
            Renewed tracking DTO
            
        Raises:
            TrackingNotFoundException: If tracking not found
        """
        logger.info(f"Renewing audience tracking {dto.tracking_id}")

        # Get tracking
        tracking = await self.tracking_repository.get_by_id(TrackingId(dto.tracking_id))
        if not tracking:
            raise TrackingNotFoundException(dto.tracking_id)

        # Create price based on currency
        if dto.currency == "XTR":
            price = TrackingPrice.for_stars()
        elif dto.currency == "RUB":
            price = TrackingPrice.for_rubles()
        else:
            price = TrackingPrice(amount=TrackingPrice.RUB_PRICE, currency=dto.currency)

        # Renew subscription
        tracking.renew(
            price=price,
            payment_id=dto.payment_id,
            duration_days=dto.duration_days,
        )

        # Save
        await self.tracking_repository.save(tracking)

        logger.info(f"Renewed audience tracking {dto.tracking_id}")

        return self._to_dto(tracking)

    def _to_dto(self, tracking: AudienceTracking) -> AudienceTrackingDTO:
        """Convert aggregate to DTO."""
        return AudienceTrackingDTO(
            tracking_id=tracking.tracking_id.value if tracking.tracking_id else int(tracking.id),
            user_id=tracking.user_id,
            target_username=tracking.target_username,
            target_user_id=tracking.target_user_id,
            is_active=tracking.is_active,
            expires_at=tracking.expires_at,
            auto_renew=tracking.auto_renew,
            amount_paid=tracking.amount_paid,
            currency=tracking.currency,
            last_follower_count=tracking.last_follower_count.value if tracking.last_follower_count else None,
            last_following_count=tracking.last_following_count.value if tracking.last_following_count else None,
            last_checked_at=tracking.last_checked_at,
            created_at=tracking.created_at,
            updated_at=tracking.updated_at,
        )

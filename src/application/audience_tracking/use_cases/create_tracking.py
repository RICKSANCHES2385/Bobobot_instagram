"""Create Audience Tracking Use Case."""

from src.application.shared.use_case import UseCase
from src.application.audience_tracking.dtos import CreateAudienceTrackingDTO, AudienceTrackingDTO
from src.domain.audience_tracking.aggregates.audience_tracking import AudienceTracking
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.domain.audience_tracking.value_objects.tracking_price import TrackingPrice
from src.domain.audience_tracking.value_objects.follower_count import FollowerCount
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId
from src.domain.audience_tracking.exceptions import (
    DuplicateTrackingException,
    FollowerLimitExceededException,
)
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CreateAudienceTrackingUseCase(UseCase[CreateAudienceTrackingDTO, AudienceTrackingDTO]):
    """Use case for creating audience tracking subscription."""

    def __init__(
        self,
        tracking_repository: AudienceTrackingRepository,
        instagram_service=None,  # Will be injected for checking follower count
    ):
        """Initialize use case.
        
        Args:
            tracking_repository: Audience tracking repository
            instagram_service: Instagram service for fetching profile data
        """
        self.tracking_repository = tracking_repository
        self.instagram_service = instagram_service

    async def execute(self, dto: CreateAudienceTrackingDTO) -> AudienceTrackingDTO:
        """Execute use case.
        
        Args:
            dto: Create tracking DTO
            
        Returns:
            Created tracking DTO
            
        Raises:
            DuplicateTrackingException: If tracking already exists
            FollowerLimitExceededException: If account has >100k followers
        """
        logger.info(
            f"Creating audience tracking for user {dto.user_id}, target @{dto.target_username}"
        )

        # Check if tracking already exists
        existing = await self.tracking_repository.get_by_user_and_target(
            dto.user_id, dto.target_username
        )
        if existing and existing.is_active:
            raise DuplicateTrackingException(dto.user_id, dto.target_username)

        # Check follower limit if Instagram service is available
        if self.instagram_service:
            try:
                profile = await self.instagram_service.fetch_profile(dto.target_username)
                follower_count = FollowerCount(profile.followers_count)
                
                if follower_count.exceeds_limit():
                    raise FollowerLimitExceededException(
                        dto.target_username,
                        follower_count.value,
                    )
            except Exception as e:
                logger.warning(f"Could not check follower limit: {e}")

        # Create price based on currency
        if dto.currency == "XTR":
            price = TrackingPrice.for_stars()
        elif dto.currency == "RUB":
            price = TrackingPrice.for_rubles()
        else:
            # For crypto, use RUB equivalent
            price = TrackingPrice(amount=TrackingPrice.RUB_PRICE, currency=dto.currency)

        # Create tracking aggregate
        tracking = AudienceTracking.create(
            user_id=dto.user_id,
            target_username=dto.target_username,
            target_user_id=dto.target_user_id,
            price=price,
            payment_id=dto.payment_id,
            duration_days=dto.duration_days,
        )

        # Save to repository
        saved_tracking = await self.tracking_repository.save(tracking)
        
        # Set tracking ID and raise created event
        saved_tracking.tracking_id = TrackingId(int(saved_tracking.id))
        saved_tracking._raise_created_event()

        logger.info(f"Created audience tracking {saved_tracking.tracking_id.value}")

        # Convert to DTO
        return self._to_dto(saved_tracking)

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

"""Get Audience Tracking Status Use Case."""

from typing import List

from src.application.shared.use_case import UseCase
from src.application.audience_tracking.dtos import AudienceTrackingDTO
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.domain.audience_tracking.aggregates.audience_tracking import AudienceTracking
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class GetAudienceTrackingStatusUseCase(UseCase[int, List[AudienceTrackingDTO]]):
    """Use case for getting user's audience tracking subscriptions."""

    def __init__(self, tracking_repository: AudienceTrackingRepository):
        """Initialize use case.
        
        Args:
            tracking_repository: Audience tracking repository
        """
        self.tracking_repository = tracking_repository

    async def execute(self, user_id: int) -> List[AudienceTrackingDTO]:
        """Execute use case.
        
        Args:
            user_id: User ID
            
        Returns:
            List of tracking DTOs
        """
        logger.info(f"Getting audience tracking status for user {user_id}")

        trackings = await self.tracking_repository.get_by_user_id(user_id)

        return [self._to_dto(tracking) for tracking in trackings]

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

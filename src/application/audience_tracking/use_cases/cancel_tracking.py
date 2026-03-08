"""Cancel Audience Tracking Use Case."""

from typing import Optional

from src.application.shared.use_case import UseCase
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId
from src.domain.audience_tracking.exceptions import TrackingNotFoundException
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CancelAudienceTrackingUseCase(UseCase[tuple[int, Optional[str]], bool]):
    """Use case for cancelling audience tracking subscription."""

    def __init__(self, tracking_repository: AudienceTrackingRepository):
        """Initialize use case.
        
        Args:
            tracking_repository: Audience tracking repository
        """
        self.tracking_repository = tracking_repository

    async def execute(self, data: tuple[int, Optional[str]]) -> bool:
        """Execute use case.
        
        Args:
            data: Tuple of (tracking_id, reason)
            
        Returns:
            True if cancelled successfully
            
        Raises:
            TrackingNotFoundException: If tracking not found
        """
        tracking_id, reason = data
        logger.info(f"Cancelling audience tracking {tracking_id}")

        # Get tracking
        tracking = await self.tracking_repository.get_by_id(TrackingId(tracking_id))
        if not tracking:
            raise TrackingNotFoundException(tracking_id)

        # Cancel subscription
        tracking.cancel(reason=reason)

        # Save
        await self.tracking_repository.save(tracking)

        logger.info(f"Cancelled audience tracking {tracking_id}")
        return True

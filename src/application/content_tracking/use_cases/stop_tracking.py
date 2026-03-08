"""Stop Tracking Use Case."""

from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.exceptions import TrackingNotFoundError


class StopTrackingUseCase:
    """Use case for stopping content tracking."""

    def __init__(self, tracking_repository: IContentTrackingRepository):
        """Initialize use case.
        
        Args:
            tracking_repository: Content tracking repository
        """
        self.tracking_repository = tracking_repository

    async def execute(self, tracking_id: str) -> None:
        """Execute use case.
        
        Args:
            tracking_id: Tracking ID
            
        Raises:
            TrackingNotFoundError: If tracking not found
        """
        # Find tracking
        tracking = await self.tracking_repository.find_by_id(TrackingId(tracking_id))
        if not tracking:
            raise TrackingNotFoundError(tracking_id)

        # Stop tracking
        tracking.stop()

        # Save tracking (or delete)
        await self.tracking_repository.delete(TrackingId(tracking_id))

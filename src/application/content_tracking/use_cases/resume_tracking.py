"""Resume Tracking Use Case."""

from src.application.content_tracking.dtos import TrackingDTO
from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.exceptions import TrackingNotFoundError


class ResumeTrackingUseCase:
    """Use case for resuming content tracking."""

    def __init__(self, tracking_repository: IContentTrackingRepository):
        """Initialize use case.
        
        Args:
            tracking_repository: Content tracking repository
        """
        self.tracking_repository = tracking_repository

    async def execute(self, tracking_id: str) -> TrackingDTO:
        """Execute use case.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            Tracking DTO
            
        Raises:
            TrackingNotFoundError: If tracking not found
        """
        # Find tracking
        tracking = await self.tracking_repository.find_by_id(TrackingId(tracking_id))
        if not tracking:
            raise TrackingNotFoundError(tracking_id)

        # Resume tracking
        tracking.resume()

        # Save tracking
        await self.tracking_repository.save(tracking)

        # Return DTO
        return TrackingDTO(
            tracking_id=tracking.tracking_id.value,
            user_id=tracking.user_id,
            instagram_user_id=tracking.instagram_user_id.value,
            instagram_username=tracking.instagram_username.value,
            content_type=tracking.content_type.value.value,
            status=tracking.status.value.value,
            check_interval_minutes=tracking.check_interval.minutes,
            notification_enabled=tracking.notification_enabled,
            last_check_at=tracking.last_check_at,
            last_content_id=tracking.last_content_id,
            created_at=tracking.created_at,
            updated_at=tracking.updated_at,
        )

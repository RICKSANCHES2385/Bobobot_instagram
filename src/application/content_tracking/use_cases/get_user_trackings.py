"""Get User Trackings Use Case."""

from src.application.content_tracking.dtos import TrackingDTO, UserTrackingsDTO
from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository


class GetUserTrackingsUseCase:
    """Use case for getting user trackings."""

    def __init__(self, tracking_repository: IContentTrackingRepository):
        """Initialize use case.
        
        Args:
            tracking_repository: Content tracking repository
        """
        self.tracking_repository = tracking_repository

    async def execute(self, user_id: str) -> UserTrackingsDTO:
        """Execute use case.
        
        Args:
            user_id: User ID
            
        Returns:
            User trackings DTO
        """
        # Find all trackings for user
        trackings = await self.tracking_repository.find_by_user_id(user_id)

        # Convert to DTOs
        tracking_dtos = [self._to_dto(tracking) for tracking in trackings]

        # Count active trackings
        active_count = sum(1 for t in trackings if t.status.is_active())

        return UserTrackingsDTO(
            user_id=user_id,
            trackings=tracking_dtos,
            total_count=len(tracking_dtos),
            active_count=active_count,
        )

    def _to_dto(self, tracking) -> TrackingDTO:
        """Convert tracking to DTO."""
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

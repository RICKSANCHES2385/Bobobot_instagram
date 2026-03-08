"""Start Tracking Use Case."""

from uuid import uuid4

from src.application.content_tracking.dtos import StartTrackingCommand, TrackingDTO
from src.domain.content_tracking.aggregates.content_tracking import ContentTracking
from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository
from src.domain.content_tracking.value_objects.tracking_id import TrackingId
from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
from src.domain.content_tracking.value_objects.check_interval import CheckInterval
from src.domain.content_tracking.exceptions import TrackingAlreadyExistsError, TrackingLimitExceededError
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
from src.infrastructure.external_services.hiker_api.hiker_api_adapter import HikerAPIAdapter


class StartTrackingUseCase:
    """Use case for starting content tracking."""

    def __init__(
        self,
        tracking_repository: IContentTrackingRepository,
        instagram_adapter: HikerAPIAdapter,
        max_trackings_per_user: int = 10,
    ):
        """Initialize use case.
        
        Args:
            tracking_repository: Content tracking repository
            instagram_adapter: Instagram API adapter
            max_trackings_per_user: Maximum trackings per user
        """
        self.tracking_repository = tracking_repository
        self.instagram_adapter = instagram_adapter
        self.max_trackings_per_user = max_trackings_per_user

    async def execute(self, command: StartTrackingCommand) -> TrackingDTO:
        """Execute use case.
        
        Args:
            command: Start tracking command
            
        Returns:
            Tracking DTO
            
        Raises:
            TrackingAlreadyExistsError: If tracking already exists
            TrackingLimitExceededError: If user exceeded tracking limit
            ProfileNotFoundError: If Instagram profile not found
        """
        # Check tracking limit
        existing_trackings = await self.tracking_repository.find_by_user_id(command.user_id)
        if len(existing_trackings) >= self.max_trackings_per_user:
            raise TrackingLimitExceededError(command.user_id, self.max_trackings_per_user)

        # Fetch Instagram profile to validate username
        username = InstagramUsername(command.instagram_username)
        profile = await self.instagram_adapter.fetch_profile_by_username(username)

        # Check if tracking already exists
        exists = await self.tracking_repository.exists(command.user_id, profile.user_id.value)
        if exists:
            raise TrackingAlreadyExistsError(command.user_id, command.instagram_username)

        # Parse content type
        content_type_enum = ContentTypeEnum(command.content_type.lower())
        content_type = ContentType(content_type_enum)

        # Create tracking
        tracking = ContentTracking.create(
            tracking_id=TrackingId(str(uuid4())),
            user_id=command.user_id,
            instagram_user_id=profile.user_id,
            instagram_username=profile.username,
            content_type=content_type,
            check_interval=CheckInterval(command.check_interval_minutes),
            notification_enabled=command.notification_enabled,
        )

        # Save tracking
        await self.tracking_repository.save(tracking)

        # Return DTO
        return self._to_dto(tracking)

    def _to_dto(self, tracking: ContentTracking) -> TrackingDTO:
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

"""Check Audience Changes Use Case."""

from typing import List

from src.application.shared.use_case import UseCase
from src.application.audience_tracking.dtos import AudienceChangeDTO
from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.domain.audience_tracking.value_objects.follower_count import FollowerCount
from src.domain.audience_tracking.value_objects.following_count import FollowingCount
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CheckAudienceChangesUseCase(UseCase[int, List[AudienceChangeDTO]]):
    """Use case for checking audience changes for a tracking subscription."""

    def __init__(
        self,
        tracking_repository: AudienceTrackingRepository,
        instagram_service=None,  # Will be injected
    ):
        """Initialize use case.
        
        Args:
            tracking_repository: Audience tracking repository
            instagram_service: Instagram service for fetching profile data
        """
        self.tracking_repository = tracking_repository
        self.instagram_service = instagram_service

    async def execute(self, tracking_id: int) -> List[AudienceChangeDTO]:
        """Execute use case.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            List of detected changes
        """
        logger.info(f"Checking audience changes for tracking {tracking_id}")

        changes = []

        # Get tracking
        tracking = await self.tracking_repository.get_by_id(TrackingId(tracking_id))
        if not tracking:
            logger.warning(f"Tracking {tracking_id} not found")
            return changes

        if not tracking.is_active or tracking.is_expired():
            logger.info(f"Tracking {tracking_id} is inactive or expired")
            return changes

        # Fetch current profile data
        if not self.instagram_service:
            logger.warning("Instagram service not available")
            return changes

        try:
            profile = await self.instagram_service.fetch_profile(tracking.target_username)
            
            # Check followers
            new_follower_count = FollowerCount(profile.followers_count)
            tracking.update_follower_count(new_follower_count)
            
            # Check if event was raised (means there was a change)
            for event in tracking.domain_events:
                if event.__class__.__name__ == "FollowersChanged":
                    changes.append(
                        AudienceChangeDTO(
                            tracking_id=tracking_id,
                            user_id=tracking.user_id,
                            target_username=tracking.target_username,
                            change_type="followers",
                            old_count=event.old_count,
                            new_count=event.new_count,
                            difference=event.difference,
                            timestamp=event.occurred_at,
                        )
                    )

            # Check following
            new_following_count = FollowingCount(profile.following_count)
            tracking.update_following_count(new_following_count)
            
            for event in tracking.domain_events:
                if event.__class__.__name__ == "FollowingChanged":
                    changes.append(
                        AudienceChangeDTO(
                            tracking_id=tracking_id,
                            user_id=tracking.user_id,
                            target_username=tracking.target_username,
                            change_type="following",
                            old_count=event.old_count,
                            new_count=event.new_count,
                            difference=event.difference,
                            timestamp=event.occurred_at,
                        )
                    )

            # Save updated tracking
            await self.tracking_repository.save(tracking)

            logger.info(f"Detected {len(changes)} changes for tracking {tracking_id}")

        except Exception as e:
            logger.error(f"Error checking audience changes: {e}")

        return changes

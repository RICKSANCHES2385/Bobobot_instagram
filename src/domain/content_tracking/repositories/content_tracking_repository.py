"""Content Tracking Repository Interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.content_tracking.aggregates.content_tracking import ContentTracking
from src.domain.content_tracking.value_objects.tracking_id import TrackingId


class IContentTrackingRepository(ABC):
    """Content tracking repository interface."""

    @abstractmethod
    async def save(self, tracking: ContentTracking) -> None:
        """Save content tracking.
        
        Args:
            tracking: Content tracking aggregate
        """
        pass

    @abstractmethod
    async def find_by_id(self, tracking_id: TrackingId) -> Optional[ContentTracking]:
        """Find content tracking by ID.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            Content tracking or None
        """
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[ContentTracking]:
        """Find all trackings for a user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            List of content trackings
        """
        pass

    @abstractmethod
    async def find_active_trackings(self) -> List[ContentTracking]:
        """Find all active trackings.
        
        Returns:
            List of active content trackings
        """
        pass

    @abstractmethod
    async def find_trackings_to_check(self) -> List[ContentTracking]:
        """Find trackings that should be checked now.
        
        Returns:
            List of content trackings ready for check
        """
        pass

    @abstractmethod
    async def delete(self, tracking_id: TrackingId) -> None:
        """Delete content tracking.
        
        Args:
            tracking_id: Tracking ID
        """
        pass

    @abstractmethod
    async def exists(self, user_id: str, instagram_user_id: str) -> bool:
        """Check if tracking exists for user and Instagram profile.
        
        Args:
            user_id: Telegram user ID
            instagram_user_id: Instagram user ID
            
        Returns:
            True if tracking exists
        """
        pass

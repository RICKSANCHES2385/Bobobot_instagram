"""Audience Tracking Repository Interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.audience_tracking.aggregates.audience_tracking import AudienceTracking
from src.domain.audience_tracking.value_objects.tracking_id import TrackingId


class AudienceTrackingRepository(ABC):
    """Repository interface for audience tracking subscriptions."""

    @abstractmethod
    async def save(self, tracking: AudienceTracking) -> AudienceTracking:
        """Save audience tracking subscription.
        
        Args:
            tracking: Audience tracking aggregate
            
        Returns:
            Saved tracking with assigned ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, tracking_id: TrackingId) -> Optional[AudienceTracking]:
        """Get tracking by ID.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            Tracking if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[AudienceTracking]:
        """Get all trackings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of trackings
        """
        pass

    @abstractmethod
    async def get_active_by_user_id(self, user_id: int) -> List[AudienceTracking]:
        """Get active trackings for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active trackings
        """
        pass

    @abstractmethod
    async def get_by_user_and_target(
        self, user_id: int, target_username: str
    ) -> Optional[AudienceTracking]:
        """Get tracking by user and target username.
        
        Args:
            user_id: User ID
            target_username: Target Instagram username
            
        Returns:
            Tracking if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_expired_subscriptions(self) -> List[AudienceTracking]:
        """Get all expired but still active subscriptions.
        
        Returns:
            List of expired subscriptions
        """
        pass

    @abstractmethod
    async def get_subscriptions_for_renewal(self) -> List[AudienceTracking]:
        """Get subscriptions that need auto-renewal.
        
        Returns:
            List of subscriptions with auto_renew enabled and expiring soon
        """
        pass

    @abstractmethod
    async def delete(self, tracking_id: TrackingId) -> bool:
        """Delete tracking subscription.
        
        Args:
            tracking_id: Tracking ID
            
        Returns:
            True if deleted, False if not found
        """
        pass

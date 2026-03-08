"""Subscription Repository Interface."""
from abc import ABC, abstractmethod
from typing import Optional
from ..aggregates.subscription import Subscription
from ..value_objects.subscription_id import SubscriptionId
from src.domain.user_management.value_objects.user_id import UserId


class SubscriptionRepository(ABC):
    """Subscription repository interface."""
    
    @abstractmethod
    async def save(self, subscription: Subscription) -> None:
        """Save subscription.
        
        Args:
            subscription: Subscription to save.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, subscription_id: SubscriptionId) -> Optional[Subscription]:
        """Get subscription by ID.
        
        Args:
            subscription_id: Subscription ID.
            
        Returns:
            Subscription if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_active_by_user_id(self, user_id: UserId) -> Optional[Subscription]:
        """Get active subscription for user.
        
        Args:
            user_id: User ID.
            
        Returns:
            Active subscription if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_all_by_user_id(self, user_id: UserId) -> list[Subscription]:
        """Get all subscriptions for user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of subscriptions.
        """
        pass
    
    @abstractmethod
    async def delete(self, subscription_id: SubscriptionId) -> None:
        """Delete subscription.
        
        Args:
            subscription_id: Subscription ID.
        """
        pass

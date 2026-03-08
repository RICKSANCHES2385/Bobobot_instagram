"""User Repository Interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from src.domain.user_management.entities.user import User
from src.domain.user_management.value_objects.user_id import UserId


class IUserRepository(ABC):
    """User repository interface."""

    @abstractmethod
    async def save(self, user: User) -> None:
        """Save user.
        
        Args:
            user: User entity
        """
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        pass

    @abstractmethod
    async def find_by_telegram_username(self, username: str) -> Optional[User]:
        """Find user by Telegram username.
        
        Args:
            username: Telegram username
            
        Returns:
            User or None
        """
        pass

    @abstractmethod
    async def find_all_active(self) -> List[User]:
        """Find all active users.
        
        Returns:
            List of active users
        """
        pass

    @abstractmethod
    async def find_users_with_expiring_subscriptions(
        self,
        expires_before: datetime,
    ) -> List[User]:
        """Find users with subscriptions expiring before date.
        
        Args:
            expires_before: Expiration date threshold
            
        Returns:
            List of users
        """
        pass

    @abstractmethod
    async def exists(self, user_id: UserId) -> bool:
        """Check if user exists.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user exists
        """
        pass

    @abstractmethod
    async def count_active_users(self) -> int:
        """Count active users.
        
        Returns:
            Number of active users
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Delete user.
        
        Args:
            user_id: User ID
        """
        pass

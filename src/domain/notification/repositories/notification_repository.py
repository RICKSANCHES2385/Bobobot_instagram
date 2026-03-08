"""Notification Repository Interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.notification.aggregates.notification import Notification
from src.domain.notification.value_objects.notification_id import NotificationId
from src.domain.notification.value_objects.notification_status import NotificationStatusEnum


class INotificationRepository(ABC):
    """Notification repository interface."""

    @abstractmethod
    async def save(self, notification: Notification) -> None:
        """Save notification.
        
        Args:
            notification: Notification aggregate
        """
        pass

    @abstractmethod
    async def find_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """Find notification by ID.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Notification or None
        """
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Find notifications for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications
            
        Returns:
            List of notifications
        """
        pass

    @abstractmethod
    async def find_pending(self, limit: int = 100) -> List[Notification]:
        """Find pending notifications.
        
        Args:
            limit: Maximum number of notifications
            
        Returns:
            List of pending notifications
        """
        pass

    @abstractmethod
    async def find_failed_retryable(self, limit: int = 50) -> List[Notification]:
        """Find failed notifications that can be retried.
        
        Args:
            limit: Maximum number of notifications
            
        Returns:
            List of retryable notifications
        """
        pass

    @abstractmethod
    async def delete(self, notification_id: NotificationId) -> None:
        """Delete notification.
        
        Args:
            notification_id: Notification ID
        """
        pass

    @abstractmethod
    async def count_by_status(self, status: NotificationStatusEnum) -> int:
        """Count notifications by status.
        
        Args:
            status: Notification status
            
        Returns:
            Count of notifications
        """
        pass

"""Notification Sender Interface."""

from abc import ABC, abstractmethod

from src.domain.notification.aggregates.notification import Notification


class INotificationSender(ABC):
    """Notification sender interface."""

    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Send notification.
        
        Args:
            notification: Notification to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass

    @abstractmethod
    async def send_batch(self, notifications: list[Notification]) -> dict[str, bool]:
        """Send multiple notifications.
        
        Args:
            notifications: List of notifications
            
        Returns:
            Dict mapping notification IDs to success status
        """
        pass

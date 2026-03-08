"""Get User Notifications Use Case."""

from typing import List

from src.domain.notification.repositories.notification_repository import INotificationRepository
from src.application.notification.dtos.notification_dto import NotificationDTO
from src.domain.notification.aggregates.notification import Notification


class GetUserNotificationsUseCase:
    """Use case for getting user notifications."""

    def __init__(self, notification_repository: INotificationRepository):
        """Initialize use case.
        
        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def execute(self, user_id: str, limit: int = 50) -> List[NotificationDTO]:
        """Execute use case.
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications
            
        Returns:
            List of notification DTOs
        """
        notifications = await self._notification_repository.find_by_user_id(
            user_id=user_id,
            limit=limit,
        )

        return [self._to_dto(n) for n in notifications]

    @staticmethod
    def _to_dto(notification: Notification) -> NotificationDTO:
        """Convert entity to DTO."""
        return NotificationDTO(
            notification_id=notification.notification_id.value,
            user_id=notification.user_id,
            notification_type=notification.notification_type.value.value,
            status=notification.status.value.value,
            priority=notification.priority.value.value,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            sent_at=notification.sent_at,
            failed_at=notification.failed_at,
            error_message=notification.error_message,
            retry_count=notification.retry_count,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
        )

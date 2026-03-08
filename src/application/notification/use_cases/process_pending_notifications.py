"""Process Pending Notifications Use Case."""

import logging
from typing import List

from src.domain.notification.repositories.notification_repository import INotificationRepository
from src.domain.notification.services.notification_sender import INotificationSender
from src.application.notification.dtos.notification_dto import NotificationDTO
from src.domain.notification.aggregates.notification import Notification


logger = logging.getLogger(__name__)


class ProcessPendingNotificationsUseCase:
    """Use case for processing pending notifications."""

    def __init__(
        self,
        notification_repository: INotificationRepository,
        notification_sender: INotificationSender,
        batch_size: int = 50,
    ):
        """Initialize use case.
        
        Args:
            notification_repository: Notification repository
            notification_sender: Notification sender service
            batch_size: Number of notifications to process at once
        """
        self._notification_repository = notification_repository
        self._notification_sender = notification_sender
        self._batch_size = batch_size

    async def execute(self) -> List[NotificationDTO]:
        """Execute use case.
        
        Returns:
            List of processed notification DTOs
        """
        # Get pending notifications
        notifications = await self._notification_repository.find_pending(
            limit=self._batch_size
        )

        if not notifications:
            logger.debug("No pending notifications to process")
            return []

        logger.info(f"Processing {len(notifications)} pending notifications")

        # Send notifications in batch
        results = await self._notification_sender.send_batch(notifications)

        # Update notification statuses
        processed = []
        for notification in notifications:
            notification_id = notification.notification_id.value
            success = results.get(notification_id, False)

            try:
                if success:
                    notification.mark_as_sent()
                else:
                    notification.mark_as_failed("Failed to send in batch")

                await self._notification_repository.save(notification)
                processed.append(self._to_dto(notification))

            except Exception as e:
                logger.error(
                    f"Error updating notification {notification_id}: {e}",
                    exc_info=True,
                )

        return processed

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

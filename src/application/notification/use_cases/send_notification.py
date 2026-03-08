"""Send Notification Use Case."""

from src.domain.notification.value_objects.notification_id import NotificationId
from src.domain.notification.repositories.notification_repository import INotificationRepository
from src.domain.notification.services.notification_sender import INotificationSender
from src.domain.notification.aggregates.notification import Notification
from src.application.notification.dtos.notification_dto import SendNotificationDTO, NotificationDTO


class SendNotificationUseCase:
    """Use case for sending a notification."""

    def __init__(
        self,
        notification_repository: INotificationRepository,
        notification_sender: INotificationSender,
    ):
        """Initialize use case.
        
        Args:
            notification_repository: Notification repository
            notification_sender: Notification sender service
        """
        self._notification_repository = notification_repository
        self._notification_sender = notification_sender

    async def execute(self, dto: SendNotificationDTO) -> NotificationDTO:
        """Execute use case.
        
        Args:
            dto: Send notification DTO
            
        Returns:
            Notification DTO
            
        Raises:
            ValueError: If notification not found
        """
        # Find notification
        notification = await self._notification_repository.find_by_id(
            NotificationId(dto.notification_id)
        )

        if notification is None:
            raise ValueError(f"Notification {dto.notification_id} not found")

        # Send notification
        try:
            success = await self._notification_sender.send(notification)

            if success:
                notification.mark_as_sent()
            else:
                notification.mark_as_failed("Failed to send notification")

        except Exception as e:
            notification.mark_as_failed(str(e))

        # Save notification
        await self._notification_repository.save(notification)

        return self._to_dto(notification)

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

"""Create Notification Use Case."""

from src.domain.notification.aggregates.notification import Notification
from src.domain.notification.value_objects.notification_id import NotificationId
from src.domain.notification.value_objects.notification_type import NotificationType, NotificationTypeEnum
from src.domain.notification.value_objects.notification_priority import NotificationPriority, NotificationPriorityEnum
from src.domain.notification.repositories.notification_repository import INotificationRepository
from src.application.notification.dtos.notification_dto import CreateNotificationDTO, NotificationDTO


class CreateNotificationUseCase:
    """Use case for creating a notification."""

    def __init__(self, notification_repository: INotificationRepository):
        """Initialize use case.
        
        Args:
            notification_repository: Notification repository
        """
        self._notification_repository = notification_repository

    async def execute(self, dto: CreateNotificationDTO) -> NotificationDTO:
        """Execute use case.
        
        Args:
            dto: Create notification DTO
            
        Returns:
            Notification DTO
        """
        # Create notification
        notification = Notification.create(
            notification_id=NotificationId.generate(),
            user_id=dto.user_id,
            notification_type=NotificationType(NotificationTypeEnum(dto.notification_type)),
            title=dto.title,
            message=dto.message,
            priority=NotificationPriority(NotificationPriorityEnum(dto.priority)),
            data=dto.data,
        )

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

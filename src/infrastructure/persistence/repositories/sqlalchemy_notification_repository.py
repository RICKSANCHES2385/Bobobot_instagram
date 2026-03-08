"""SQLAlchemy Notification Repository."""

from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.notification.repositories.notification_repository import INotificationRepository
from src.domain.notification.aggregates.notification import Notification
from src.domain.notification.value_objects.notification_id import NotificationId
from src.domain.notification.value_objects.notification_type import NotificationType, NotificationTypeEnum
from src.domain.notification.value_objects.notification_status import NotificationStatus, NotificationStatusEnum
from src.domain.notification.value_objects.notification_priority import NotificationPriority, NotificationPriorityEnum
from src.infrastructure.persistence.models.notification_model import (
    NotificationModel,
    NotificationTypeDB,
    NotificationStatusDB,
    NotificationPriorityDB,
)


class SQLAlchemyNotificationRepository(INotificationRepository):
    """SQLAlchemy implementation of notification repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, notification: Notification) -> None:
        """Save notification."""
        model = await self._session.get(NotificationModel, notification.notification_id.value)

        if model is None:
            # Create new
            model = self._to_model(notification)
            self._session.add(model)
        else:
            # Update existing
            self._update_model(model, notification)

        await self._session.flush()

    async def find_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """Find notification by ID."""
        model = await self._session.get(NotificationModel, notification_id.value)
        return self._to_entity(model) if model else None

    async def find_by_user_id(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Find notifications for user."""
        stmt = select(NotificationModel).where(
            NotificationModel.user_id == user_id
        ).order_by(NotificationModel.created_at.desc()).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def find_pending(self, limit: int = 100) -> List[Notification]:
        """Find pending notifications."""
        stmt = select(NotificationModel).where(
            NotificationModel.status == NotificationStatusDB.PENDING
        ).order_by(
            NotificationModel.priority.desc(),
            NotificationModel.created_at.asc()
        ).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def find_failed_retryable(self, limit: int = 50) -> List[Notification]:
        """Find failed notifications that can be retried."""
        stmt = select(NotificationModel).where(
            and_(
                NotificationModel.status == NotificationStatusDB.FAILED,
                NotificationModel.retry_count < NotificationModel.max_retries,
            )
        ).order_by(NotificationModel.failed_at.asc()).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def delete(self, notification_id: NotificationId) -> None:
        """Delete notification."""
        model = await self._session.get(NotificationModel, notification_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    async def count_by_status(self, status: NotificationStatusEnum) -> int:
        """Count notifications by status."""
        status_db = self._map_status_to_db(NotificationStatus(status))
        stmt = select(func.count()).select_from(NotificationModel).where(
            NotificationModel.status == status_db
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    def _to_model(self, notification: Notification) -> NotificationModel:
        """Convert entity to model."""
        return NotificationModel(
            id=notification.notification_id.value,
            user_id=notification.user_id,
            notification_type=self._map_type_to_db(notification.notification_type),
            status=self._map_status_to_db(notification.status),
            priority=self._map_priority_to_db(notification.priority),
            title=notification.title,
            message=notification.message,
            data=notification.data,
            sent_at=notification.sent_at,
            failed_at=notification.failed_at,
            error_message=notification.error_message,
            retry_count=notification.retry_count,
            max_retries=notification.max_retries,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
        )

    def _update_model(self, model: NotificationModel, notification: Notification) -> None:
        """Update model from entity."""
        model.status = self._map_status_to_db(notification.status)
        model.sent_at = notification.sent_at
        model.failed_at = notification.failed_at
        model.error_message = notification.error_message
        model.retry_count = notification.retry_count
        model.updated_at = notification.updated_at

    def _to_entity(self, model: NotificationModel) -> Notification:
        """Convert model to entity."""
        notification = Notification(
            id=model.id,
            notification_id=NotificationId(model.id),
            user_id=model.user_id,
            notification_type=self._map_type_from_db(model.notification_type),
            status=self._map_status_from_db(model.status),
            priority=self._map_priority_from_db(model.priority),
            title=model.title,
            message=model.message,
            data=model.data or {},
            sent_at=model.sent_at,
            failed_at=model.failed_at,
            error_message=model.error_message,
            retry_count=model.retry_count,
            max_retries=model.max_retries,
        )
        notification.created_at = model.created_at
        notification.updated_at = model.updated_at
        return notification

    @staticmethod
    def _map_type_to_db(notification_type: NotificationType) -> NotificationTypeDB:
        """Map domain type to database enum."""
        mapping = {
            NotificationTypeEnum.CONTENT_UPDATE: NotificationTypeDB.CONTENT_UPDATE,
            NotificationTypeEnum.SUBSCRIPTION_EXPIRING: NotificationTypeDB.SUBSCRIPTION_EXPIRING,
            NotificationTypeEnum.SUBSCRIPTION_EXPIRED: NotificationTypeDB.SUBSCRIPTION_EXPIRED,
            NotificationTypeEnum.PAYMENT_SUCCESS: NotificationTypeDB.PAYMENT_SUCCESS,
            NotificationTypeEnum.PAYMENT_FAILED: NotificationTypeDB.PAYMENT_FAILED,
            NotificationTypeEnum.SYSTEM_MESSAGE: NotificationTypeDB.SYSTEM_MESSAGE,
        }
        return mapping[notification_type.value]

    @staticmethod
    def _map_type_from_db(notification_type: NotificationTypeDB) -> NotificationType:
        """Map database enum to domain type."""
        mapping = {
            NotificationTypeDB.CONTENT_UPDATE: NotificationTypeEnum.CONTENT_UPDATE,
            NotificationTypeDB.SUBSCRIPTION_EXPIRING: NotificationTypeEnum.SUBSCRIPTION_EXPIRING,
            NotificationTypeDB.SUBSCRIPTION_EXPIRED: NotificationTypeEnum.SUBSCRIPTION_EXPIRED,
            NotificationTypeDB.PAYMENT_SUCCESS: NotificationTypeEnum.PAYMENT_SUCCESS,
            NotificationTypeDB.PAYMENT_FAILED: NotificationTypeEnum.PAYMENT_FAILED,
            NotificationTypeDB.SYSTEM_MESSAGE: NotificationTypeEnum.SYSTEM_MESSAGE,
        }
        return NotificationType(mapping[notification_type])

    @staticmethod
    def _map_status_to_db(status: NotificationStatus) -> NotificationStatusDB:
        """Map domain status to database enum."""
        mapping = {
            NotificationStatusEnum.PENDING: NotificationStatusDB.PENDING,
            NotificationStatusEnum.SENT: NotificationStatusDB.SENT,
            NotificationStatusEnum.FAILED: NotificationStatusDB.FAILED,
            NotificationStatusEnum.CANCELLED: NotificationStatusDB.CANCELLED,
        }
        return mapping[status.value]

    @staticmethod
    def _map_status_from_db(status: NotificationStatusDB) -> NotificationStatus:
        """Map database enum to domain status."""
        mapping = {
            NotificationStatusDB.PENDING: NotificationStatusEnum.PENDING,
            NotificationStatusDB.SENT: NotificationStatusEnum.SENT,
            NotificationStatusDB.FAILED: NotificationStatusEnum.FAILED,
            NotificationStatusDB.CANCELLED: NotificationStatusEnum.CANCELLED,
        }
        return NotificationStatus(mapping[status])

    @staticmethod
    def _map_priority_to_db(priority: NotificationPriority) -> NotificationPriorityDB:
        """Map domain priority to database enum."""
        mapping = {
            NotificationPriorityEnum.LOW: NotificationPriorityDB.LOW,
            NotificationPriorityEnum.NORMAL: NotificationPriorityDB.NORMAL,
            NotificationPriorityEnum.HIGH: NotificationPriorityDB.HIGH,
            NotificationPriorityEnum.URGENT: NotificationPriorityDB.URGENT,
        }
        return mapping[priority.value]

    @staticmethod
    def _map_priority_from_db(priority: NotificationPriorityDB) -> NotificationPriority:
        """Map database enum to domain priority."""
        mapping = {
            NotificationPriorityDB.LOW: NotificationPriorityEnum.LOW,
            NotificationPriorityDB.NORMAL: NotificationPriorityEnum.NORMAL,
            NotificationPriorityDB.HIGH: NotificationPriorityEnum.HIGH,
            NotificationPriorityDB.URGENT: NotificationPriorityEnum.URGENT,
        }
        return NotificationPriority(mapping[priority])

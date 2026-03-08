"""Unit of Work pattern implementation."""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user_management.repositories.user_repository import IUserRepository
from src.domain.subscription.repositories.subscription_repository import SubscriptionRepository
from src.domain.payment.repositories.payment_repository import IPaymentRepository
from src.domain.content_tracking.repositories.content_tracking_repository import IContentTrackingRepository
from src.domain.notification.repositories.notification_repository import INotificationRepository
from src.domain.audience_tracking.repositories.audience_tracking_repository import AudienceTrackingRepository
from src.domain.referral.repositories.referral_repository import ReferralRepository

from .repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from .repositories.sqlalchemy_subscription_repository import SQLAlchemySubscriptionRepository
from .repositories.sqlalchemy_payment_repository import SQLAlchemyPaymentRepository
from .repositories.sqlalchemy_content_tracking_repository import SQLAlchemyContentTrackingRepository
from .repositories.sqlalchemy_notification_repository import SQLAlchemyNotificationRepository
from .repositories.sqlalchemy_audience_tracking_repository import SqlAlchemyAudienceTrackingRepository
from .repositories.sqlalchemy_referral_repository import SqlAlchemyReferralRepository


class IUnitOfWork(Protocol):
    """Unit of Work interface."""
    
    users: IUserRepository
    subscriptions: SubscriptionRepository
    payments: IPaymentRepository
    content_trackings: IContentTrackingRepository
    notifications: INotificationRepository
    audience_trackings: AudienceTrackingRepository
    referrals: ReferralRepository
    
    async def commit(self) -> None:
        """Commit the transaction."""
        ...
    
    async def rollback(self) -> None:
        """Rollback the transaction."""
        ...


class SQLAlchemyUnitOfWork:
    """SQLAlchemy implementation of Unit of Work."""
    
    def __init__(self, session: AsyncSession):
        """Initialize unit of work with session.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session
        self.users = SQLAlchemyUserRepository(session)
        self.subscriptions = SQLAlchemySubscriptionRepository(session)
        self.payments = SQLAlchemyPaymentRepository(session)
        self.content_trackings = SQLAlchemyContentTrackingRepository(session)
        self.notifications = SQLAlchemyNotificationRepository(session)
        self.audience_trackings = SqlAlchemyAudienceTrackingRepository(session)
        self.referrals = SqlAlchemyReferralRepository(session)
    
    async def commit(self) -> None:
        """Commit the transaction."""
        await self._session.commit()
    
    async def rollback(self) -> None:
        """Rollback the transaction."""
        await self._session.rollback()

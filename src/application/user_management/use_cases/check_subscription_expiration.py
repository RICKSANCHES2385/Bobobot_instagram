"""Check Subscription Expiration Use Case."""

from datetime import datetime, timedelta
from typing import List

from src.domain.user_management.repositories.user_repository import IUserRepository
from src.application.user_management.dtos.user_dto import UserDTO
from src.domain.user_management.entities.user import User


class CheckSubscriptionExpirationUseCase:
    """Use case for checking and expiring subscriptions."""

    def __init__(self, user_repository: IUserRepository):
        """Initialize use case.
        
        Args:
            user_repository: User repository
        """
        self._user_repository = user_repository

    async def execute(self, days_ahead: int = 0) -> List[UserDTO]:
        """Execute use case.
        
        Args:
            days_ahead: Check subscriptions expiring in N days (0 = expired now)
            
        Returns:
            List of users with expired/expiring subscriptions
        """
        expires_before = datetime.utcnow() + timedelta(days=days_ahead)

        # Find users with expiring subscriptions
        users = await self._user_repository.find_users_with_expiring_subscriptions(
            expires_before=expires_before
        )

        expired_users = []

        for user in users:
            # Expire subscription if needed
            if user.subscription_expires_at and user.subscription_expires_at <= datetime.utcnow():
                if not user.subscription_status.is_expired():
                    user.expire_subscription()
                    await self._user_repository.save(user)

            expired_users.append(self._to_dto(user))

        return expired_users

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        """Convert entity to DTO."""
        return UserDTO(
            user_id=user.user_id.value,
            telegram_username=user.telegram_username.value,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value.value,
            subscription_status=user.subscription_status.value.value,
            subscription_expires_at=user.subscription_expires_at,
            is_active=user.is_active,
            last_activity_at=user.last_activity_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

"""SQLAlchemy User Repository."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user_management.repositories.user_repository import IUserRepository
from src.domain.user_management.entities.user import User
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.user_management.value_objects.user_role import UserRole, UserRoleEnum
from src.domain.user_management.value_objects.telegram_username import TelegramUsername
from src.domain.user_management.value_objects.subscription_status import (
    SubscriptionStatus,
    SubscriptionStatusEnum,
)
from src.infrastructure.persistence.models.user_model import (
    UserModel,
    UserRoleDB,
    SubscriptionStatusDB,
)


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of user repository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, user: User) -> None:
        """Save user."""
        model = await self._session.get(UserModel, user.user_id.value)

        if model is None:
            # Create new
            model = self._to_model(user)
            self._session.add(model)
        else:
            # Update existing
            self._update_model(model, user)

        await self._session.flush()

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        model = await self._session.get(UserModel, user_id.value)
        return self._to_entity(model) if model else None

    async def find_by_telegram_username(self, username: str) -> Optional[User]:
        """Find user by Telegram username."""
        stmt = select(UserModel).where(UserModel.telegram_username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all_active(self) -> List[User]:
        """Find all active users."""
        stmt = select(UserModel).where(UserModel.is_active == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def find_users_with_expiring_subscriptions(
        self,
        expires_before: datetime,
    ) -> List[User]:
        """Find users with subscriptions expiring before date."""
        stmt = select(UserModel).where(
            and_(
                UserModel.subscription_expires_at.isnot(None),
                UserModel.subscription_expires_at <= expires_before,
                UserModel.subscription_status.in_([
                    SubscriptionStatusDB.ACTIVE,
                    SubscriptionStatusDB.TRIAL,
                ]),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def exists(self, user_id: UserId) -> bool:
        """Check if user exists."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_active_users(self) -> int:
        """Count active users."""
        stmt = select(func.count()).select_from(UserModel).where(UserModel.is_active == True)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def delete(self, user_id: UserId) -> None:
        """Delete user."""
        model = await self._session.get(UserModel, user_id.value)
        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _to_model(self, user: User) -> UserModel:
        """Convert entity to model."""
        return UserModel(
            id=user.user_id.value,
            telegram_username=user.telegram_username.value,
            first_name=user.first_name,
            last_name=user.last_name,
            role=self._map_role_to_db(user.role),
            subscription_status=self._map_subscription_status_to_db(user.subscription_status),
            subscription_expires_at=user.subscription_expires_at,
            is_active=user.is_active,
            last_activity_at=user.last_activity_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    def _update_model(self, model: UserModel, user: User) -> None:
        """Update model from entity."""
        model.telegram_username = user.telegram_username.value
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.role = self._map_role_to_db(user.role)
        model.subscription_status = self._map_subscription_status_to_db(user.subscription_status)
        model.subscription_expires_at = user.subscription_expires_at
        model.is_active = user.is_active
        model.last_activity_at = user.last_activity_at
        model.updated_at = user.updated_at

    def _to_entity(self, model: UserModel) -> User:
        """Convert model to entity."""
        user = User(
            id=model.id,
            user_id=UserId(model.id),
            telegram_username=TelegramUsername(model.telegram_username),
            first_name=model.first_name,
            last_name=model.last_name,
            role=self._map_role_from_db(model.role),
            subscription_status=self._map_subscription_status_from_db(model.subscription_status),
            subscription_expires_at=model.subscription_expires_at,
            is_active=model.is_active,
            last_activity_at=model.last_activity_at,
        )
        user.created_at = model.created_at
        user.updated_at = model.updated_at
        return user

    @staticmethod
    def _map_role_to_db(role: UserRole) -> UserRoleDB:
        """Map domain role to database enum."""
        mapping = {
            UserRoleEnum.USER: UserRoleDB.USER,
            UserRoleEnum.PREMIUM: UserRoleDB.PREMIUM,
            UserRoleEnum.ADMIN: UserRoleDB.ADMIN,
        }
        return mapping[role.value]

    @staticmethod
    def _map_role_from_db(role: UserRoleDB) -> UserRole:
        """Map database enum to domain role."""
        mapping = {
            UserRoleDB.USER: UserRoleEnum.USER,
            UserRoleDB.PREMIUM: UserRoleEnum.PREMIUM,
            UserRoleDB.ADMIN: UserRoleEnum.ADMIN,
        }
        return UserRole(mapping[role])

    @staticmethod
    def _map_subscription_status_to_db(status: SubscriptionStatus) -> SubscriptionStatusDB:
        """Map domain subscription status to database enum."""
        mapping = {
            SubscriptionStatusEnum.ACTIVE: SubscriptionStatusDB.ACTIVE,
            SubscriptionStatusEnum.EXPIRED: SubscriptionStatusDB.EXPIRED,
            SubscriptionStatusEnum.CANCELLED: SubscriptionStatusDB.CANCELLED,
            SubscriptionStatusEnum.TRIAL: SubscriptionStatusDB.TRIAL,
        }
        return mapping[status.value]

    @staticmethod
    def _map_subscription_status_from_db(status: SubscriptionStatusDB) -> SubscriptionStatus:
        """Map database enum to domain subscription status."""
        mapping = {
            SubscriptionStatusDB.ACTIVE: SubscriptionStatusEnum.ACTIVE,
            SubscriptionStatusDB.EXPIRED: SubscriptionStatusEnum.EXPIRED,
            SubscriptionStatusDB.CANCELLED: SubscriptionStatusEnum.CANCELLED,
            SubscriptionStatusDB.TRIAL: SubscriptionStatusEnum.TRIAL,
        }
        return SubscriptionStatus(mapping[status])

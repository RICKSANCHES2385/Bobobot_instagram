"""Activate Subscription Use Case."""

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.domain.user_management.value_objects.user_id import UserId
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.domain.user_management.entities.user import User
from src.application.user_management.dtos.user_dto import ActivateSubscriptionDTO, UserDTO


class ActivateSubscriptionUseCase:
    """Use case for activating user subscription."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """Initialize use case.
        
        Args:
            session_factory: SQLAlchemy session factory
        """
        self._session_factory = session_factory

    async def execute(self, dto: ActivateSubscriptionDTO) -> UserDTO:
        """Execute use case.
        
        Args:
            dto: Activate subscription DTO
            
        Returns:
            User DTO
            
        Raises:
            ValueError: If user not found
        """
        async with self._session_factory() as session:
            user_repository = SQLAlchemyUserRepository(session)
            user = await user_repository.find_by_id(UserId(int(dto.user_id)))

            if user is None:
                raise ValueError(f"User {dto.user_id} not found")

            # Activate subscription
            user.activate_subscription(
                expires_at=dto.expires_at,
                is_trial=dto.is_trial,
            )

            # Save user
            await user_repository.save(user)
            await session.commit()

            return self._to_dto(user)

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

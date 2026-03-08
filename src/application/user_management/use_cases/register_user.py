"""Register User Use Case."""

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.domain.user_management.entities.user import User
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.user_management.value_objects.telegram_username import TelegramUsername
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.application.user_management.dtos.user_dto import RegisterUserDTO, UserDTO


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """Initialize use case.
        
        Args:
            session_factory: SQLAlchemy session factory
        """
        self._session_factory = session_factory

    async def execute(self, dto: RegisterUserDTO) -> UserDTO:
        """Execute use case.
        
        Args:
            dto: Register user DTO
            
        Returns:
            User DTO
            
        Raises:
            ValueError: If user already exists
        """
        async with self._session_factory() as session:
            user_repository = SQLAlchemyUserRepository(session)
            user_id = UserId(int(dto.user_id))

            # Check if user already exists
            if await user_repository.exists(user_id):
                # Return existing user instead of raising error
                existing_user = await user_repository.find_by_id(user_id)
                if existing_user:
                    return self._to_dto(existing_user)
                raise ValueError(f"User {dto.user_id} exists but cannot be retrieved")

            # Create user
            user = User.register(
                user_id=user_id,
                telegram_username=TelegramUsername(dto.telegram_username) if dto.telegram_username else TelegramUsername(""),
                first_name=dto.first_name,
                last_name=dto.last_name,
            )

            # Save user
            await user_repository.save(user)
            await session.commit()

            return self._to_dto(user)

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        """Convert entity to DTO."""
        return UserDTO(
            user_id=str(user.user_id.value),
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

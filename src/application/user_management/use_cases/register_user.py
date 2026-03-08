"""Register User Use Case."""

from src.domain.user_management.entities.user import User
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.user_management.value_objects.telegram_username import TelegramUsername
from src.domain.user_management.repositories.user_repository import IUserRepository
from src.application.user_management.dtos.user_dto import RegisterUserDTO, UserDTO


class RegisterUserUseCase:
    """Use case for registering a new user."""

    def __init__(self, user_repository: IUserRepository):
        """Initialize use case.
        
        Args:
            user_repository: User repository
        """
        self._user_repository = user_repository

    async def execute(self, dto: RegisterUserDTO) -> UserDTO:
        """Execute use case.
        
        Args:
            dto: Register user DTO
            
        Returns:
            User DTO
            
        Raises:
            ValueError: If user already exists
        """
        user_id = UserId(int(dto.user_id))

        # Check if user already exists
        if await self._user_repository.exists(user_id):
            raise ValueError(f"User {dto.user_id} already exists")

        # Create user
        user = User.register(
            user_id=user_id,
            telegram_username=TelegramUsername(dto.telegram_username),
            first_name=dto.first_name,
            last_name=dto.last_name,
        )

        # Save user
        await self._user_repository.save(user)

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

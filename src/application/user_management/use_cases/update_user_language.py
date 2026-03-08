"""Update User Language Use Case."""
from ..dtos import UpdateUserLanguageCommand, UserDTO
from ...shared.use_case import UseCase
from ....domain.user_management.value_objects.telegram_id import TelegramId
from ....domain.user_management.value_objects.language import Language, LanguageCode
from ....domain.user_management.repositories.user_repository import UserRepository
from ....domain.user_management.exceptions import UserNotFoundException


class UpdateUserLanguageUseCase(UseCase[UpdateUserLanguageCommand, UserDTO]):
    """Update user language."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize use case.
        
        Args:
            user_repository: User repository.
        """
        self.user_repository = user_repository
    
    async def execute(self, command: UpdateUserLanguageCommand) -> UserDTO:
        """Execute use case.
        
        Args:
            command: Update language command.
            
        Returns:
            User DTO.
            
        Raises:
            UserNotFoundException: If user not found.
        """
        telegram_id = TelegramId(value=command.telegram_id)
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if user is None:
            raise UserNotFoundException(identifier=f"telegram_id={command.telegram_id}")
        
        # Change language
        new_language = Language(code=LanguageCode(command.language_code))
        user.change_language(new_language)
        
        # Save user
        await self.user_repository.save(user)
        
        return UserDTO(
            id=user.id.value,
            telegram_id=user.telegram_id.value,
            username=user.username.value,
            language_code=user.language.code.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )

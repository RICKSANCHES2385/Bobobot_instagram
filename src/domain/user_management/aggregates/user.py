"""User Aggregate Root."""
from dataclasses import dataclass
from src.domain.shared.entities.base import AggregateRoot
from ..value_objects.user_id import UserId
from ..value_objects.telegram_id import TelegramId
from ..value_objects.username import Username
from ..value_objects.language import Language
from ..events.user_events import UserRegistered, UserLanguageChanged


@dataclass(eq=False)
class User(AggregateRoot):
    """User aggregate root.
    
    Represents a bot user with their settings and preferences.
    """
    
    telegram_id: TelegramId = None  # type: ignore
    username: Username = None  # type: ignore
    language: Language = None  # type: ignore
    is_active: bool = True
    
    @staticmethod
    def register(
        user_id: UserId,
        telegram_id: TelegramId,
        username: Username,
        language: Language | None = None
    ) -> 'User':
        """Register a new user.
        
        Args:
            user_id: User ID.
            telegram_id: Telegram ID.
            username: Username.
            language: Language (optional, defaults to Russian).
            
        Returns:
            New User instance.
        """
        if language is None:
            language = Language.default()
        
        user = User(
            id=user_id,
            telegram_id=telegram_id,
            username=username,
            language=language
        )
        
        user.add_domain_event(
            UserRegistered(
                user_id=user_id.value,
                telegram_id=telegram_id.value,
                username=username.value
            )
        )
        
        return user
    
    def change_language(self, new_language: Language) -> None:
        """Change user language.
        
        Args:
            new_language: New language.
        """
        if self.language == new_language:
            return
        
        old_language = self.language
        self.language = new_language
        self._touch()
        
        self.add_domain_event(
            UserLanguageChanged(
                user_id=self.id.value,
                old_language=old_language.code.value,
                new_language=new_language.code.value
            )
        )
    
    def deactivate(self) -> None:
        """Deactivate user."""
        self.is_active = False
        self._touch()
    
    def activate(self) -> None:
        """Activate user."""
        self.is_active = True
        self._touch()

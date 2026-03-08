"""User Management DTOs."""
from dataclasses import dataclass


@dataclass
class RegisterUserCommand:
    """Register user command."""
    telegram_id: int
    username: str
    language_code: str | None = None


@dataclass
class UpdateUserLanguageCommand:
    """Update user language command."""
    telegram_id: int
    language_code: str


@dataclass
class UserDTO:
    """User data transfer object."""
    id: int
    telegram_id: int
    username: str
    language_code: str
    is_active: bool
    created_at: str
    updated_at: str

"""User Management Domain Exceptions."""
from src.domain.shared.exceptions.base import DomainException


class UserAlreadyExistsException(DomainException):
    """User already exists."""
    
    def __init__(self, telegram_id: int):
        super().__init__(
            message=f"User with Telegram ID {telegram_id} already exists",
            code="USER_ALREADY_EXISTS"
        )


class UserNotFoundException(DomainException):
    """User not found."""
    
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User not found: {identifier}",
            code="USER_NOT_FOUND"
        )

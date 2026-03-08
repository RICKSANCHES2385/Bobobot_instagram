"""Instagram Integration Exceptions."""
from src.domain.shared.exceptions.base import DomainException


class ProfileNotFoundException(DomainException):
    """Exception raised when Instagram profile is not found."""
    
    def __init__(self, username: str):
        super().__init__(
            message=f"Instagram profile not found: {username}",
            code="PROFILE_NOT_FOUND"
        )


class ProfileIsPrivateException(DomainException):
    """Exception raised when Instagram profile is private."""
    
    def __init__(self, username: str):
        super().__init__(
            message=f"Instagram profile is private: {username}",
            code="PROFILE_IS_PRIVATE"
        )


class RateLimitExceededException(DomainException):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED"
        )


class InvalidInstagramDataException(DomainException):
    """Exception raised when Instagram data is invalid."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="INVALID_INSTAGRAM_DATA"
        )

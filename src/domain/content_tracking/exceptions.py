"""Content Tracking Exceptions."""

from src.domain.shared.exceptions.base import DomainException


class TrackingNotFoundError(DomainException):
    """Raised when tracking is not found."""

    def __init__(self, tracking_id: str):
        super().__init__(f"Tracking not found: {tracking_id}")


class TrackingAlreadyExistsError(DomainException):
    """Raised when tracking already exists."""

    def __init__(self, user_id: str, instagram_username: str):
        super().__init__(f"Tracking already exists for user {user_id} and @{instagram_username}")


class InvalidTrackingStateError(DomainException):
    """Raised when tracking is in invalid state for operation."""

    def __init__(self, message: str):
        super().__init__(message)


class TrackingLimitExceededError(DomainException):
    """Raised when user exceeds tracking limit."""

    def __init__(self, user_id: str, limit: int):
        super().__init__(f"User {user_id} exceeded tracking limit of {limit}")

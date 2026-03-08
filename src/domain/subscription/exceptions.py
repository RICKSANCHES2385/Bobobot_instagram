"""Subscription Domain Exceptions."""
from src.domain.shared.exceptions.base import DomainException


class SubscriptionNotFoundException(DomainException):
    """Subscription not found."""
    
    def __init__(self, identifier: str):
        super().__init__(
            message=f"Subscription not found: {identifier}",
            code="SUBSCRIPTION_NOT_FOUND"
        )


class SubscriptionAlreadyExistsException(DomainException):
    """Active subscription already exists."""
    
    def __init__(self, user_id: int):
        super().__init__(
            message=f"Active subscription already exists for user {user_id}",
            code="SUBSCRIPTION_ALREADY_EXISTS"
        )


class InvalidSubscriptionOperationException(DomainException):
    """Invalid subscription operation."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="INVALID_SUBSCRIPTION_OPERATION"
        )

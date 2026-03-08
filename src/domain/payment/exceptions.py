"""Payment domain exceptions."""
from ..shared.exceptions.base import DomainException


class PaymentException(DomainException):
    """Base exception for payment domain."""
    
    pass


class InvalidPaymentStateException(PaymentException):
    """Exception raised when payment state transition is invalid."""
    
    def __init__(self, current_status: str, action: str):
        """Initialize exception."""
        super().__init__(
            f"Cannot {action} payment with status {current_status}"
        )


class PaymentNotFoundException(PaymentException):
    """Exception raised when payment is not found."""
    
    def __init__(self, payment_id: int):
        """Initialize exception."""
        super().__init__(f"Payment with ID {payment_id} not found")


class InvalidPaymentAmountException(PaymentException):
    """Exception raised when payment amount is invalid."""
    
    def __init__(self, amount: float):
        """Initialize exception."""
        super().__init__(f"Invalid payment amount: {amount}")


class PaymentProcessingException(PaymentException):
    """Exception raised when payment processing fails."""
    
    def __init__(self, reason: str):
        """Initialize exception."""
        super().__init__(f"Payment processing failed: {reason}")

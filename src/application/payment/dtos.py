"""Payment DTOs."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class CreatePaymentCommand:
    """Command to create a payment."""
    
    user_id: int
    amount: float
    currency: str
    method: str


@dataclass
class ProcessPaymentCommand:
    """Command to process a payment."""
    
    payment_id: UUID


@dataclass
class CompletePaymentCommand:
    """Command to complete a payment."""
    
    payment_id: UUID
    transaction_id: Optional[str] = None


@dataclass
class FailPaymentCommand:
    """Command to fail a payment."""
    
    payment_id: UUID
    reason: str


@dataclass
class RefundPaymentCommand:
    """Command to refund a payment."""
    
    payment_id: UUID
    refund_amount: float
    reason: Optional[str] = None


@dataclass
class PaymentDTO:
    """Payment data transfer object."""
    
    id: UUID
    user_id: int
    amount: float
    currency: str
    method: str
    status: str
    transaction_id: Optional[str]
    failure_reason: Optional[str]
    refund_amount: Optional[float]
    created_at: datetime
    updated_at: datetime

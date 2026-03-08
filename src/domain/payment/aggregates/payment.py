"""Payment aggregate root."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ...shared.entities.base import AggregateRoot
from ...shared.value_objects.money import Money
from ...user_management.value_objects.user_id import UserId
from ..value_objects.payment_id import PaymentId
from ..value_objects.payment_status import PaymentStatus
from ..value_objects.payment_method import PaymentMethod
from ..events.payment_events import (
    PaymentCreated,
    PaymentProcessing,
    PaymentCompleted,
    PaymentFailed,
    PaymentCancelled,
    PaymentRefunded
)
from ..exceptions import (
    InvalidPaymentStateException,
    InvalidPaymentAmountException
)


@dataclass(eq=False)
class Payment(AggregateRoot):
    """Payment aggregate root."""
    
    user_id: UserId = None
    amount: Money = None
    method: PaymentMethod = None
    status: PaymentStatus = None
    transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None
    refund_amount: Optional[Money] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @staticmethod
    def create(
        user_id: UserId,
        amount: Money,
        method: PaymentMethod
    ) -> 'Payment':
        """Create a new payment.
        
        Args:
            user_id: User ID who makes the payment
            amount: Payment amount
            method: Payment method
            
        Returns:
            Payment: New payment instance
            
        Raises:
            InvalidPaymentAmountException: If amount is invalid
        """
        if amount.amount <= 0:
            raise InvalidPaymentAmountException(amount.amount)
        
        from uuid import uuid4
        payment_id = PaymentId(uuid4())
        
        payment = Payment(
            id=payment_id,
            user_id=user_id,
            amount=amount,
            method=method,
            status=PaymentStatus.pending()
        )
        
        payment.add_domain_event(
            PaymentCreated(
                payment_id=payment_id.value,
                user_id=user_id.value,
                amount=amount.amount,
                currency=amount.currency,
                method=method.value.value
            )
        )
        
        return payment
    
    def process(self) -> None:
        """Start processing the payment.
        
        Raises:
            InvalidPaymentStateException: If payment cannot be processed
        """
        if not self.status.can_process():
            raise InvalidPaymentStateException(
                self.status.value.value,
                "process"
            )
        
        self.status = PaymentStatus.processing()
        self.updated_at = datetime.utcnow()
        
        self.add_domain_event(
            PaymentProcessing(payment_id=self.id.value)
        )
    
    def complete(self, transaction_id: Optional[str] = None) -> None:
        """Complete the payment.
        
        Args:
            transaction_id: External transaction ID
            
        Raises:
            InvalidPaymentStateException: If payment cannot be completed
        """
        if not self.status.can_complete():
            raise InvalidPaymentStateException(
                self.status.value.value,
                "complete"
            )
        
        self.status = PaymentStatus.completed()
        self.transaction_id = transaction_id
        self.updated_at = datetime.utcnow()
        
        self.add_domain_event(
            PaymentCompleted(
                payment_id=self.id.value,
                transaction_id=transaction_id
            )
        )
    
    def fail(self, reason: str) -> None:
        """Fail the payment.
        
        Args:
            reason: Failure reason
            
        Raises:
            InvalidPaymentStateException: If payment cannot fail
        """
        if not self.status.can_fail():
            raise InvalidPaymentStateException(
                self.status.value.value,
                "fail"
            )
        
        self.status = PaymentStatus.failed()
        self.failure_reason = reason
        self.updated_at = datetime.utcnow()
        
        self.add_domain_event(
            PaymentFailed(
                payment_id=self.id.value,
                reason=reason
            )
        )
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the payment.
        
        Args:
            reason: Cancellation reason
            
        Raises:
            InvalidPaymentStateException: If payment cannot be cancelled
        """
        if not self.status.can_cancel():
            raise InvalidPaymentStateException(
                self.status.value.value,
                "cancel"
            )
        
        self.status = PaymentStatus.cancelled()
        self.failure_reason = reason
        self.updated_at = datetime.utcnow()
        
        self.add_domain_event(
            PaymentCancelled(
                payment_id=self.id.value,
                reason=reason
            )
        )
    
    def refund(self, refund_amount: Money, reason: Optional[str] = None) -> None:
        """Refund the payment.
        
        Args:
            refund_amount: Amount to refund
            reason: Refund reason
            
        Raises:
            InvalidPaymentStateException: If payment cannot be refunded
            InvalidPaymentAmountException: If refund amount is invalid
        """
        if not self.status.can_refund():
            raise InvalidPaymentStateException(
                self.status.value.value,
                "refund"
            )
        
        if refund_amount.amount <= 0 or refund_amount.amount > self.amount.amount:
            raise InvalidPaymentAmountException(refund_amount.amount)
        
        if refund_amount.currency != self.amount.currency:
            raise InvalidPaymentAmountException(refund_amount.amount)
        
        self.status = PaymentStatus.refunded()
        self.refund_amount = refund_amount
        self.failure_reason = reason
        self.updated_at = datetime.utcnow()
        
        self.add_domain_event(
            PaymentRefunded(
                payment_id=self.id.value,
                refund_amount=refund_amount.amount,
                reason=reason
            )
        )

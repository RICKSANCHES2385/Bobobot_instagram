"""Refund payment use case."""
from dataclasses import dataclass

from ...shared.use_case import UseCase
from ..dtos import RefundPaymentCommand, PaymentDTO
from ....domain.payment.repositories.payment_repository import IPaymentRepository
from ....domain.payment.value_objects.payment_id import PaymentId
from ....domain.payment.exceptions import PaymentNotFoundException
from ....domain.shared.value_objects.money import Money


@dataclass
class RefundPaymentUseCase(UseCase[RefundPaymentCommand, PaymentDTO]):
    """Use case for refunding a payment."""
    
    payment_repository: IPaymentRepository
    
    async def execute(self, command: RefundPaymentCommand) -> PaymentDTO:
        """Execute the use case.
        
        Args:
            command: Refund payment command
            
        Returns:
            PaymentDTO: Updated payment data
            
        Raises:
            PaymentNotFoundException: If payment not found
            InvalidPaymentStateException: If payment cannot be refunded
            InvalidPaymentAmountException: If refund amount is invalid
        """
        # Get payment
        payment_id = PaymentId(value=command.payment_id)
        payment = await self.payment_repository.get_by_id(payment_id)
        
        if not payment:
            raise PaymentNotFoundException(payment_id.value)
        
        # Create refund amount with same currency as original payment
        refund_amount = Money(
            amount=command.refund_amount,
            currency=payment.amount.currency
        )
        
        # Refund payment
        payment.refund(
            refund_amount=refund_amount,
            reason=command.reason
        )
        
        # Save payment
        await self.payment_repository.save(payment)
        
        # Return DTO
        return PaymentDTO(
            id=payment.id.value,
            user_id=payment.user_id.value,
            amount=payment.amount.amount,
            currency=payment.amount.currency,
            method=payment.method.value.value,
            status=payment.status.value.value,
            transaction_id=payment.transaction_id,
            failure_reason=payment.failure_reason,
            refund_amount=payment.refund_amount.amount if payment.refund_amount else None,
            created_at=payment.created_at,
            updated_at=payment.updated_at
        )

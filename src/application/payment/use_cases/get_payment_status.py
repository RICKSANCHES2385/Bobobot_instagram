"""Get payment status use case."""
from dataclasses import dataclass
from uuid import UUID

from ...shared.use_case import UseCase
from ..dtos import PaymentDTO
from ....domain.payment.repositories.payment_repository import IPaymentRepository
from ....domain.payment.value_objects.payment_id import PaymentId
from ....domain.payment.exceptions import PaymentNotFoundException


@dataclass
class GetPaymentStatusUseCase(UseCase[UUID, PaymentDTO]):
    """Use case for getting payment status."""
    
    payment_repository: IPaymentRepository
    
    async def execute(self, payment_id: UUID) -> PaymentDTO:
        """Execute the use case.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            PaymentDTO: Payment data
            
        Raises:
            PaymentNotFoundException: If payment not found
        """
        # Get payment
        payment_id_vo = PaymentId(value=payment_id)
        payment = await self.payment_repository.get_by_id(payment_id_vo)
        
        if not payment:
            raise PaymentNotFoundException(payment_id)
        
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

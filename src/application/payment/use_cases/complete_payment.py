"""Complete payment use case."""
from dataclasses import dataclass
from typing import Optional

from ...shared.use_case import UseCase
from ..dtos import CompletePaymentCommand, PaymentDTO
from ....domain.payment.repositories.payment_repository import IPaymentRepository
from ....domain.payment.value_objects.payment_id import PaymentId
from ....domain.payment.exceptions import PaymentNotFoundException


@dataclass
class CompletePaymentUseCase(UseCase[CompletePaymentCommand, PaymentDTO]):
    """Use case for completing a payment."""
    
    payment_repository: IPaymentRepository
    process_referral_reward_use_case: Optional[object] = None  # ProcessReferralRewardUseCase
    
    async def execute(self, command: CompletePaymentCommand) -> PaymentDTO:
        """Execute the use case.
        
        Args:
            command: Complete payment command
            
        Returns:
            PaymentDTO: Updated payment data
            
        Raises:
            PaymentNotFoundException: If payment not found
            InvalidPaymentStateException: If payment cannot be completed
        """
        # Get payment
        payment_id = PaymentId(value=command.payment_id)
        payment = await self.payment_repository.get_by_id(payment_id)
        
        if not payment:
            raise PaymentNotFoundException(payment_id.value)
        
        # Complete payment
        payment.complete(transaction_id=command.transaction_id)
        
        # Save payment
        await self.payment_repository.save(payment)
        
        # Process referral reward if applicable
        if self.process_referral_reward_use_case:
            try:
                await self.process_referral_reward_use_case.execute(
                    referred_user_id=int(payment.user_id.value),
                    payment_id=int(payment.id.value),
                    payment_amount=payment.amount.amount,
                    currency=payment.amount.currency,
                )
            except Exception:
                # Don't fail payment if referral processing fails
                pass
        
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

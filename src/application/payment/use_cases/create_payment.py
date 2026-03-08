"""Create payment use case."""
from dataclasses import dataclass

from ...shared.use_case import UseCase
from ..dtos import CreatePaymentCommand, PaymentDTO
from ....domain.payment.aggregates.payment import Payment
from ....domain.payment.repositories.payment_repository import IPaymentRepository
from ....domain.payment.value_objects.payment_method import PaymentMethod, PaymentMethodEnum
from ....domain.shared.value_objects.money import Money
from ....domain.user_management.value_objects.user_id import UserId


@dataclass
class CreatePaymentUseCase(UseCase[CreatePaymentCommand, PaymentDTO]):
    """Use case for creating a payment."""
    
    payment_repository: IPaymentRepository
    
    async def execute(self, command: CreatePaymentCommand) -> PaymentDTO:
        """Execute the use case.
        
        Args:
            command: Create payment command
            
        Returns:
            PaymentDTO: Created payment data
            
        Raises:
            InvalidPaymentAmountException: If amount is invalid
            ValueError: If currency or method is invalid
        """
        # Create value objects
        user_id = UserId(value=command.user_id)
        amount = Money(amount=command.amount, currency=command.currency)
        
        # Validate and create payment method
        try:
            method_enum = PaymentMethodEnum(command.method)
            method = PaymentMethod(value=method_enum)
        except ValueError:
            raise ValueError(f"Invalid payment method: {command.method}")
        
        # Create payment
        payment = Payment.create(
            user_id=user_id,
            amount=amount,
            method=method
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

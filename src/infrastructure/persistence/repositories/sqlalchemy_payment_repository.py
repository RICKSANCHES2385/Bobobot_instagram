"""SQLAlchemy Payment Repository implementation."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....domain.payment.aggregates.payment import Payment
from ....domain.payment.repositories.payment_repository import IPaymentRepository
from ....domain.payment.value_objects.payment_id import PaymentId
from ....domain.payment.value_objects.payment_status import PaymentStatus, PaymentStatusEnum
from ....domain.payment.value_objects.payment_method import PaymentMethod, PaymentMethodEnum
from ....domain.shared.value_objects.money import Money
from ....domain.user_management.value_objects.user_id import UserId
from ..models.payment_model import PaymentModel


class SQLAlchemyPaymentRepository(IPaymentRepository):
    """SQLAlchemy implementation of Payment Repository."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session
    
    async def save(self, payment: Payment) -> None:
        """Save payment.
        
        Args:
            payment: Payment to save
        """
        # Check if payment exists
        stmt = select(PaymentModel).where(PaymentModel.id == payment.id.value)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing payment
            existing.user_id = str(payment.user_id.value)
            existing.amount = payment.amount.amount
            existing.currency = payment.amount.currency
            existing.method = payment.method.value.value
            existing.status = payment.status.value.value
            existing.transaction_id = payment.transaction_id
            existing.failure_reason = payment.failure_reason
            existing.refund_amount = payment.refund_amount.amount if payment.refund_amount else None
            existing.updated_at = payment.updated_at
        else:
            # Create new payment
            model = PaymentModel(
                id=payment.id.value,
                user_id=str(payment.user_id.value),
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
            self._session.add(model)
        
        await self._session.flush()
    
    async def get_by_id(self, payment_id: PaymentId) -> Optional[Payment]:
        """Get payment by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment if found, None otherwise
        """
        stmt = select(PaymentModel).where(PaymentModel.id == payment_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return self._to_domain(model)
    
    async def get_by_user_id(self, user_id: UserId) -> List[Payment]:
        """Get all payments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of payments
        """
        stmt = select(PaymentModel).where(PaymentModel.user_id == str(user_id.value)).order_by(PaymentModel.created_at.desc())
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_domain(model) for model in models]
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID.
        
        Args:
            transaction_id: External transaction ID
            
        Returns:
            Payment if found, None otherwise
        """
        stmt = select(PaymentModel).where(PaymentModel.transaction_id == transaction_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return self._to_domain(model)
    
    def _to_domain(self, model: PaymentModel) -> Payment:
        """Convert model to domain entity.
        
        Args:
            model: Payment model
            
        Returns:
            Payment domain entity
        """
        # Create payment aggregate
        payment = Payment(
            id=PaymentId(value=model.id),
            user_id=UserId(value=int(model.user_id)),
            amount=Money(amount=model.amount, currency=model.currency),
            method=PaymentMethod(value=PaymentMethodEnum(model.method)),
            status=PaymentStatus(value=PaymentStatusEnum(model.status)),
            transaction_id=model.transaction_id,
            failure_reason=model.failure_reason,
            refund_amount=Money(amount=model.refund_amount, currency=model.currency) if model.refund_amount else None,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
        
        return payment

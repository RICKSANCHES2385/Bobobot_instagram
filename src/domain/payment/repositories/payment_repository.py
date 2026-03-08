"""Payment repository interface."""
from abc import ABC, abstractmethod
from typing import Optional, List

from ..aggregates.payment import Payment
from ..value_objects.payment_id import PaymentId
from ...user_management.value_objects.user_id import UserId


class IPaymentRepository(ABC):
    """Payment repository interface."""
    
    @abstractmethod
    async def save(self, payment: Payment) -> None:
        """Save payment.
        
        Args:
            payment: Payment to save
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, payment_id: PaymentId) -> Optional[Payment]:
        """Get payment by ID.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[Payment]:
        """Get all payments for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of payments
        """
        pass
    
    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID.
        
        Args:
            transaction_id: External transaction ID
            
        Returns:
            Payment if found, None otherwise
        """
        pass

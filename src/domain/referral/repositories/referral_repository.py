"""Referral repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.referral.aggregates.referral import Referral
from src.domain.referral.value_objects.referral_code import ReferralCode


class ReferralRepository(ABC):
    """Repository interface for Referral aggregate."""

    @abstractmethod
    async def save(self, referral: Referral) -> Referral:
        """Save or update a referral.
        
        Args:
            referral: Referral aggregate to save
            
        Returns:
            Saved referral with updated ID
        """
        pass

    @abstractmethod
    async def find_by_id(self, referral_id: int) -> Optional[Referral]:
        """Find referral by ID.
        
        Args:
            referral_id: Referral ID
            
        Returns:
            Referral if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_referrer_user_id(
        self, referrer_user_id: int
    ) -> Optional[Referral]:
        """Find referral by referrer user ID.
        
        Args:
            referrer_user_id: Referrer user ID
            
        Returns:
            Referral if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_referral_code(
        self, referral_code: ReferralCode
    ) -> Optional[Referral]:
        """Find referral by referral code.
        
        Args:
            referral_code: Referral code
            
        Returns:
            Referral if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_referred_user_id(
        self, referred_user_id: int
    ) -> Optional[Referral]:
        """Find referral by referred user ID.
        
        Args:
            referred_user_id: Referred user ID
            
        Returns:
            Referral if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_referral_stats(
        self, referrer_user_id: int
    ) -> dict:
        """Get referral statistics for a user.
        
        Args:
            referrer_user_id: Referrer user ID
            
        Returns:
            Dictionary with stats:
            - total_referrals: Total number of referrals
            - active_referrals: Number of referrals who made payments
            - total_earned: Total amount earned
            - total_paid_out: Total amount paid out
            - available_balance: Available balance for payout
        """
        pass

    @abstractmethod
    async def exists_by_referral_code(self, referral_code: ReferralCode) -> bool:
        """Check if referral code already exists.
        
        Args:
            referral_code: Referral code to check
            
        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, referral_id: int) -> None:
        """Delete a referral.
        
        Args:
            referral_id: Referral ID to delete
        """
        pass

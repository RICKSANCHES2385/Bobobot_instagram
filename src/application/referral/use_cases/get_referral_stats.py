"""Get referral stats use case."""

from src.application.referral.dtos import ReferralStatsDTO
from src.domain.referral.repositories.referral_repository import ReferralRepository


class GetReferralStatsUseCase:
    """Use case for getting referral statistics for a user."""

    def __init__(self, referral_repository: ReferralRepository):
        self._referral_repository = referral_repository

    async def execute(self, user_id: int) -> ReferralStatsDTO:
        """Get referral statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            ReferralStatsDTO with statistics
            
        Raises:
            ValueError: If user doesn't have a referral code
        """
        # Find referral by user ID
        referral = await self._referral_repository.find_by_referrer_user_id(user_id)

        if not referral:
            raise ValueError(f"User {user_id} doesn't have a referral code")

        # Get stats from repository
        stats = await self._referral_repository.get_referral_stats(user_id)

        # Build DTO
        return ReferralStatsDTO(
            referrer_user_id=user_id,
            referral_code=str(referral.referral_code),
            total_referrals=stats.get("total_referrals", 0),
            active_referrals=stats.get("active_referrals", 0),
            total_earned=stats.get("total_earned", 0),
            total_paid_out=stats.get("total_paid_out", 0),
            available_balance=stats.get("available_balance", 0),
            currency=referral.total_earned.currency.value,
            first_referral_at=referral.applied_at,
            last_payout_at=referral.last_payout_at,
        )

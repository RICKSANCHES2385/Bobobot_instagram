"""Request referral payout use case."""

from src.domain.referral.aggregates.referral import Referral
from src.domain.referral.repositories.referral_repository import ReferralRepository


class RequestReferralPayoutUseCase:
    """Use case for requesting a payout of referral rewards."""

    def __init__(self, referral_repository: ReferralRepository):
        self._referral_repository = referral_repository

    async def execute(self, user_id: int) -> Referral:
        """Request payout of referral rewards.
        
        Args:
            user_id: User ID requesting payout
            
        Returns:
            Updated Referral aggregate
            
        Raises:
            ValueError: If user doesn't have a referral code
            MinimumPayoutNotReachedError: If balance is below minimum
        """
        # Find referral by user ID
        referral = await self._referral_repository.find_by_referrer_user_id(user_id)

        if not referral:
            raise ValueError(f"User {user_id} doesn't have a referral code")

        # Request payout (will raise exception if below minimum)
        referral.request_payout()

        # Save updated referral
        return await self._referral_repository.save(referral)

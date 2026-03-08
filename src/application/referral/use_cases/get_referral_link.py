"""Get referral link use case."""

from src.application.referral.dtos import ReferralLinkDTO
from src.domain.referral.repositories.referral_repository import ReferralRepository


class GetReferralLinkUseCase:
    """Use case for getting a user's referral link."""

    def __init__(
        self,
        referral_repository: ReferralRepository,
        bot_username: str,
    ):
        self._referral_repository = referral_repository
        self._bot_username = bot_username

    async def execute(self, user_id: int) -> ReferralLinkDTO:
        """Get referral link for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            ReferralLinkDTO with link details
            
        Raises:
            ValueError: If user doesn't have a referral code
        """
        # Find referral by user ID
        referral = await self._referral_repository.find_by_referrer_user_id(user_id)

        if not referral:
            raise ValueError(f"User {user_id} doesn't have a referral code")

        # Generate deep link
        referral_code = str(referral.referral_code)
        referral_link = f"https://t.me/{self._bot_username}?start={referral_code}"

        return ReferralLinkDTO(
            referral_code=referral_code,
            referral_link=referral_link,
            bot_username=self._bot_username,
        )

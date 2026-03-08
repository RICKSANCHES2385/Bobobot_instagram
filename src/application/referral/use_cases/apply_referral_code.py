"""Apply referral code use case."""

from src.application.referral.dtos import ApplyReferralCodeDTO
from src.domain.referral.aggregates.referral import Referral
from src.domain.referral.exceptions import InvalidReferralCodeError
from src.domain.referral.repositories.referral_repository import ReferralRepository
from src.domain.referral.value_objects.referral_code import ReferralCode


class ApplyReferralCodeUseCase:
    """Use case for applying a referral code to a new user."""

    def __init__(self, referral_repository: ReferralRepository):
        self._referral_repository = referral_repository

    async def execute(self, dto: ApplyReferralCodeDTO) -> Referral:
        """Apply referral code to a new user.
        
        Args:
            dto: DTO with referred_user_id and referral_code
            
        Returns:
            Updated Referral aggregate
            
        Raises:
            InvalidReferralCodeError: If referral code doesn't exist
        """
        # Check if user already used a referral code
        existing_referral = await self._referral_repository.find_by_referred_user_id(
            dto.referred_user_id
        )
        if existing_referral:
            raise InvalidReferralCodeError(
                "User has already used a referral code"
            )

        # Find referral by code
        referral_code = ReferralCode(dto.referral_code)
        referral = await self._referral_repository.find_by_referral_code(
            referral_code
        )

        if not referral:
            raise InvalidReferralCodeError(
                f"Referral code '{dto.referral_code}' not found"
            )

        # Apply referral code to user
        referral.apply_to_user(dto.referred_user_id)

        # Save updated referral
        return await self._referral_repository.save(referral)

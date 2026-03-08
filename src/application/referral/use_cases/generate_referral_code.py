"""Generate referral code use case."""

import secrets
import string
from typing import Optional

from src.application.referral.dtos import GenerateReferralCodeDTO
from src.domain.referral.aggregates.referral import Referral
from src.domain.referral.repositories.referral_repository import ReferralRepository
from src.domain.referral.value_objects.referral_code import ReferralCode
from src.domain.shared.value_objects.money import Currency


class GenerateReferralCodeUseCase:
    """Use case for generating a unique referral code for a user."""

    def __init__(self, referral_repository: ReferralRepository):
        self._referral_repository = referral_repository

    async def execute(self, dto: GenerateReferralCodeDTO) -> Referral:
        """Generate a unique referral code for a user.
        
        Args:
            dto: DTO with user_id and currency
            
        Returns:
            Created Referral aggregate
        """
        # Check if user already has a referral code
        existing_referral = await self._referral_repository.find_by_referrer_user_id(
            dto.user_id
        )
        if existing_referral:
            return existing_referral

        # Generate unique referral code
        referral_code = await self._generate_unique_code()

        # Create referral
        currency = Currency(dto.currency)
        referral = Referral.create(
            referrer_user_id=dto.user_id,
            referral_code=referral_code,
            currency=currency,
        )

        # Save referral
        return await self._referral_repository.save(referral)

    async def _generate_unique_code(self) -> ReferralCode:
        """Generate a unique referral code.
        
        Returns:
            Unique ReferralCode
        """
        max_attempts = 10
        for _ in range(max_attempts):
            # Generate random 8-character code
            code_str = "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(8)
            )
            code = ReferralCode(code_str)

            # Check if code already exists
            exists = await self._referral_repository.exists_by_referral_code(code)
            if not exists:
                return code

        # Fallback: use timestamp-based code
        import time
        timestamp_code = f"REF{int(time.time()) % 1000000}"
        return ReferralCode(timestamp_code)

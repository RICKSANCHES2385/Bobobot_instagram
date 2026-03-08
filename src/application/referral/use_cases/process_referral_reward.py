"""Process referral reward use case."""

from decimal import Decimal
from typing import Optional

from src.application.referral.dtos import ReferralRewardDTO
from src.domain.referral.repositories.referral_repository import ReferralRepository
from src.domain.shared.value_objects.money import Currency


class ProcessReferralRewardUseCase:
    """Use case for processing referral reward when referred user makes first payment."""

    def __init__(
        self,
        referral_repository: ReferralRepository,
        referral_reward_earned_handler: Optional[object] = None,
    ):
        self._referral_repository = referral_repository
        self._reward_earned_handler = referral_reward_earned_handler

    async def execute(
        self,
        referred_user_id: int,
        payment_id: int,
        payment_amount: Decimal,
        currency: str,
    ) -> ReferralRewardDTO:
        """Process referral reward for a payment.
        
        Args:
            referred_user_id: ID of user who made payment
            payment_id: Payment ID
            payment_amount: Payment amount
            currency: Currency code
            
        Returns:
            ReferralRewardDTO with reward details, or None if no referral
        """
        # Find referral by referred user ID
        referral = await self._referral_repository.find_by_referred_user_id(
            referred_user_id
        )

        if not referral:
            # User wasn't referred by anyone
            return None

        # Check if this is the first payment (reward not yet earned)
        if referral.has_earned_reward():
            # Already earned reward from this referral
            return None

        # Earn reward
        currency_obj = Currency(currency)
        referral.earn_reward(
            payment_id=payment_id,
            payment_amount=payment_amount,
            currency=currency_obj,
        )

        # Save updated referral
        await self._referral_repository.save(referral)

        # Handle domain events (send notifications)
        if self._reward_earned_handler and referral._domain_events:
            for event in referral._domain_events:
                try:
                    await self._reward_earned_handler.handle(event)
                except Exception:
                    # Don't fail if notification fails
                    pass

        # Return reward details
        return ReferralRewardDTO(
            payment_amount=payment_amount,
            commission_rate=referral.commission_rate.rate,
            reward_amount=referral.commission_rate.calculate_reward(payment_amount),
            currency=currency,
        )

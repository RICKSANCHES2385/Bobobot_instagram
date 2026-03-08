"""Calculate referral reward use case."""

from decimal import Decimal

from src.application.referral.dtos import ReferralRewardDTO
from src.domain.referral.value_objects.commission_rate import CommissionRate
from src.domain.shared.value_objects.currency import Currency


class CalculateReferralRewardUseCase:
    """Use case for calculating referral reward from a payment."""

    def execute(
        self,
        payment_amount: Decimal,
        currency: str = "RUB",
    ) -> ReferralRewardDTO:
        """Calculate referral reward.
        
        Args:
            payment_amount: Payment amount
            currency: Currency code
            
        Returns:
            ReferralRewardDTO with calculation details
        """
        commission_rate = CommissionRate.default()
        reward_amount = commission_rate.calculate_reward(payment_amount)

        return ReferralRewardDTO(
            payment_amount=payment_amount,
            commission_rate=commission_rate.rate,
            reward_amount=reward_amount,
            currency=currency,
        )

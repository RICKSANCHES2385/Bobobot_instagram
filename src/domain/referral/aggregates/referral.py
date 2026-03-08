"""Referral aggregate root."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.domain.referral.events.referral_events import (
    ReferralApplied,
    ReferralPayoutRequested,
    ReferralRewardEarned,
)
from src.domain.referral.exceptions import (
    MinimumPayoutNotReachedError,
    ReferralCodeAlreadyUsedError,
    SelfReferralNotAllowedError,
)
from src.domain.referral.value_objects.commission_rate import CommissionRate
from src.domain.referral.value_objects.referral_code import ReferralCode
from src.domain.referral.value_objects.referral_reward import ReferralReward
from src.domain.shared.entities.base import AggregateRoot
from src.domain.shared.value_objects.money import Currency


@dataclass
class Referral(AggregateRoot):
    """Referral aggregate root.
    
    Represents a referral relationship between a referrer and a referred user.
    
    Business rules:
    - User cannot use their own referral code
    - Referral code can only be used once per user
    - Referrer earns 5% commission from first payment
    - Minimum payout: 1000 RUB
    """

    referrer_user_id: int = field(default=0)
    referral_code: ReferralCode = field(default=None)
    commission_rate: CommissionRate = field(default=None)
    total_earned: ReferralReward = field(default=None)
    total_paid_out: ReferralReward = field(default=None)
    referred_user_id: Optional[int] = None
    applied_at: Optional[datetime] = None
    first_payment_at: Optional[datetime] = None
    last_payout_at: Optional[datetime] = None
    referral_count: int = 0

    @classmethod
    def create(
        cls,
        referrer_user_id: int,
        referral_code: ReferralCode,
        currency: Currency = Currency.RUB,
    ) -> "Referral":
        """Create a new referral with default commission rate."""
        return cls(
            referrer_user_id=referrer_user_id,
            referral_code=referral_code,
            commission_rate=CommissionRate.default(),
            total_earned=ReferralReward(amount=Decimal("0"), currency=currency),
            total_paid_out=ReferralReward(amount=Decimal("0"), currency=currency),
        )

    def apply_to_user(self, referred_user_id: int) -> None:
        """Apply referral code to a new user.
        
        Args:
            referred_user_id: ID of the user applying the code
            
        Raises:
            SelfReferralNotAllowedError: If user tries to use their own code
            ReferralCodeAlreadyUsedError: If user already used a referral code
        """
        if referred_user_id == self.referrer_user_id:
            raise SelfReferralNotAllowedError(
                "Cannot use your own referral code"
            )

        if self.referred_user_id is not None:
            raise ReferralCodeAlreadyUsedError(
                "This referral code has already been used by this user"
            )

        self.referred_user_id = referred_user_id
        self.applied_at = datetime.utcnow()
        self.referral_count += 1

        self._add_domain_event(
            ReferralApplied(
                referrer_user_id=self.referrer_user_id,
                referred_user_id=referred_user_id,
                referral_code=str(self.referral_code),
                applied_at=self.applied_at,
            )
        )

    def earn_reward(
        self,
        payment_id: int,
        payment_amount: Decimal,
        currency: Currency,
    ) -> None:
        """Earn reward from referral's first payment.
        
        Args:
            payment_id: ID of the payment
            payment_amount: Amount of the payment
            currency: Currency of the payment
        """
        reward_amount = self.commission_rate.calculate_reward(payment_amount)
        reward = ReferralReward(amount=reward_amount, currency=currency)

        # Add to total earned
        if self.total_earned.currency == currency:
            self.total_earned = self.total_earned.add(reward)
        else:
            # If different currency, create new reward
            # In production, you'd handle currency conversion
            self.total_earned = reward

        self.first_payment_at = datetime.utcnow()

        self._add_domain_event(
            ReferralRewardEarned(
                referrer_user_id=self.referrer_user_id,
                referred_user_id=self.referred_user_id,
                payment_id=payment_id,
                reward_amount=reward_amount,
                currency=currency.value,
                earned_at=self.first_payment_at,
            )
        )

    def request_payout(self) -> None:
        """Request payout of earned rewards.
        
        Raises:
            MinimumPayoutNotReachedError: If earned amount is below minimum
        """
        available_amount = self._calculate_available_payout()

        if not available_amount.is_payout_available():
            raise MinimumPayoutNotReachedError(
                f"Minimum payout is {ReferralReward.MINIMUM_PAYOUT_RUB} RUB. "
                f"Current balance: {available_amount}"
            )

        self.total_paid_out = self.total_paid_out.add(available_amount)
        self.last_payout_at = datetime.utcnow()

        self._add_domain_event(
            ReferralPayoutRequested(
                referrer_user_id=self.referrer_user_id,
                payout_amount=available_amount.amount,
                currency=available_amount.currency.value,
                requested_at=self.last_payout_at,
            )
        )

    def _calculate_available_payout(self) -> ReferralReward:
        """Calculate available payout amount (earned - paid out)."""
        available = self.total_earned.amount - self.total_paid_out.amount
        return ReferralReward(
            amount=available,
            currency=self.total_earned.currency,
        )

    def get_available_balance(self) -> ReferralReward:
        """Get current available balance for payout."""
        return self._calculate_available_payout()

    def has_referred_user(self) -> bool:
        """Check if this referral has been applied to a user."""
        return self.referred_user_id is not None

    def has_earned_reward(self) -> bool:
        """Check if referrer has earned any rewards."""
        return self.total_earned.amount > Decimal("0")

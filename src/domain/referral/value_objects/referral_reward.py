"""Referral reward value object."""

from dataclasses import dataclass
from decimal import Decimal

from src.domain.referral.exceptions import InvalidRewardAmountError
from src.domain.shared.value_objects.currency import Currency


@dataclass(frozen=True)
class ReferralReward:
    """Referral reward value object.
    
    Business rules:
    - Amount must be positive
    - Minimum payout: 1000 RUB (or equivalent)
    - Supports multiple currencies (RUB, XTR, USDT, TON)
    """

    amount: Decimal
    currency: Currency

    MINIMUM_PAYOUT_RUB = Decimal("1000")  # 1000₽

    def __post_init__(self) -> None:
        """Validate reward amount."""
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

        if self.amount < Decimal("0"):
            raise InvalidRewardAmountError("Reward amount cannot be negative")

    def is_payout_available(self) -> bool:
        """Check if reward amount meets minimum payout threshold.
        
        For simplicity, we check against RUB equivalent.
        In production, you'd convert to RUB using exchange rates.
        """
        if self.currency.value == "RUB":
            return self.amount >= self.MINIMUM_PAYOUT_RUB
        
        # For other currencies, assume conversion is handled elsewhere
        # This is a simplified check
        return self.amount >= Decimal("10")  # Minimum for crypto

    def add(self, other: "ReferralReward") -> "ReferralReward":
        """Add another reward (must be same currency)."""
        if self.currency != other.currency:
            raise InvalidRewardAmountError(
                "Cannot add rewards with different currencies"
            )
        return ReferralReward(
            amount=self.amount + other.amount,
            currency=self.currency,
        )

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.amount} {self.currency.value}"

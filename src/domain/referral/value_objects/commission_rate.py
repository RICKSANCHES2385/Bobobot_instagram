"""Commission rate value object."""

from dataclasses import dataclass
from decimal import Decimal

from src.domain.referral.exceptions import InvalidCommissionRateError


@dataclass(frozen=True)
class CommissionRate:
    """Commission rate value object.
    
    Business rules:
    - Default rate is 5% (0.05)
    - Must be between 0% and 100%
    - Stored as decimal (0.05 = 5%)
    """

    rate: Decimal

    DEFAULT_RATE = Decimal("0.05")  # 5%

    def __post_init__(self) -> None:
        """Validate commission rate."""
        if not isinstance(self.rate, Decimal):
            object.__setattr__(self, "rate", Decimal(str(self.rate)))

        if self.rate < Decimal("0") or self.rate > Decimal("1"):
            raise InvalidCommissionRateError(
                "Commission rate must be between 0% and 100%"
            )

    @classmethod
    def default(cls) -> "CommissionRate":
        """Create default commission rate (5%)."""
        return cls(rate=cls.DEFAULT_RATE)

    def calculate_reward(self, payment_amount: Decimal) -> Decimal:
        """Calculate reward amount based on payment."""
        return payment_amount * self.rate

    def as_percentage(self) -> Decimal:
        """Return rate as percentage (0.05 -> 5)."""
        return self.rate * Decimal("100")

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.as_percentage()}%"

"""Tracking price value object."""

from dataclasses import dataclass
from decimal import Decimal

from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TrackingPrice(BaseValueObject):
    """Represents the price for audience tracking subscription.
    
    Business rule: 576 Telegram Stars + 129 RUB/month equivalent.
    """

    amount: Decimal
    currency: str

    # Pricing constants
    STARS_PRICE = 576
    RUB_PRICE = Decimal("129.00")

    def __post_init__(self) -> None:
        """Validate tracking price."""
        if not isinstance(self.amount, (Decimal, int, float)):
            raise ValueError("Price amount must be numeric")
        
        # Convert to Decimal if needed
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        
        if self.amount < 0:
            raise ValueError("Price cannot be negative")
        
        if not isinstance(self.currency, str):
            raise ValueError("Currency must be a string")
        
        valid_currencies = {"RUB", "XTR", "USDT", "TON"}
        if self.currency not in valid_currencies:
            raise ValueError(f"Currency must be one of {valid_currencies}")

    @classmethod
    def for_stars(cls) -> "TrackingPrice":
        """Create price in Telegram Stars."""
        return cls(amount=Decimal(cls.STARS_PRICE), currency="XTR")

    @classmethod
    def for_rubles(cls) -> "TrackingPrice":
        """Create price in Russian Rubles."""
        return cls(amount=cls.RUB_PRICE, currency="RUB")

    def __str__(self) -> str:
        """String representation."""
        if self.currency == "XTR":
            return f"{int(self.amount)} ⭐"
        return f"{self.amount} {self.currency}"

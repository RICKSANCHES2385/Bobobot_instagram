"""Money Value Object."""
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from .base import BaseValueObject


class Currency(str, Enum):
    """Supported currencies."""
    XTR = "XTR"  # Telegram Stars
    RUB = "RUB"  # Russian Ruble
    TON = "TON"  # TON Coin
    USDT = "USDT"  # Tether


@dataclass(frozen=True)
class Money(BaseValueObject):
    """Money value object with amount and currency."""
    
    amount: Decimal
    currency: Currency
    
    def _validate(self) -> None:
        """Validate money value."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money values."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add money with different currencies: "
                f"{self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money values."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract money with different currencies: "
                f"{self.currency} and {other.currency}"
            )
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        return Money(result_amount, self.currency)
    
    def multiply(self, factor: int | float | Decimal) -> 'Money':
        """Multiply money by a factor."""
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        result_amount = self.amount * factor
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        return Money(result_amount, self.currency)
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.amount} {self.currency.value}"

"""Currency value object."""
from dataclasses import dataclass
from enum import Enum

from ...shared.value_objects.base import BaseValueObject


class CurrencyEnum(str, Enum):
    """Currency enumeration."""
    
    XTR = "XTR"  # Telegram Stars
    RUB = "RUB"  # Russian Ruble
    TON = "TON"  # TON Coin
    USDT = "USDT"  # Tether


@dataclass(frozen=True)
class Currency(BaseValueObject):
    """Currency value object."""
    
    value: CurrencyEnum
    
    @staticmethod
    def xtr() -> 'Currency':
        """Create XTR (Telegram Stars) currency."""
        return Currency(value=CurrencyEnum.XTR)
    
    @staticmethod
    def rub() -> 'Currency':
        """Create RUB (Russian Ruble) currency."""
        return Currency(value=CurrencyEnum.RUB)
    
    @staticmethod
    def ton() -> 'Currency':
        """Create TON currency."""
        return Currency(value=CurrencyEnum.TON)
    
    @staticmethod
    def usdt() -> 'Currency':
        """Create USDT currency."""
        return Currency(value=CurrencyEnum.USDT)
    
    def is_xtr(self) -> bool:
        """Check if currency is XTR."""
        return self.value == CurrencyEnum.XTR
    
    def is_rub(self) -> bool:
        """Check if currency is RUB."""
        return self.value == CurrencyEnum.RUB
    
    def is_ton(self) -> bool:
        """Check if currency is TON."""
        return self.value == CurrencyEnum.TON
    
    def is_usdt(self) -> bool:
        """Check if currency is USDT."""
        return self.value == CurrencyEnum.USDT
    
    def is_crypto(self) -> bool:
        """Check if currency is cryptocurrency."""
        return self.value in [CurrencyEnum.TON, CurrencyEnum.USDT]

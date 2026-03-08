"""Payment method value object."""
from dataclasses import dataclass
from enum import Enum

from ...shared.value_objects.base import BaseValueObject


class PaymentMethodEnum(str, Enum):
    """Payment method enumeration."""
    
    TELEGRAM_STARS = "telegram_stars"
    ROBOKASSA = "robokassa"
    CRYPTO_BOT = "crypto_bot"


@dataclass(frozen=True)
class PaymentMethod(BaseValueObject):
    """Payment method value object."""
    
    value: PaymentMethodEnum
    
    @staticmethod
    def telegram_stars() -> 'PaymentMethod':
        """Create Telegram Stars payment method."""
        return PaymentMethod(value=PaymentMethodEnum.TELEGRAM_STARS)
    
    @staticmethod
    def robokassa() -> 'PaymentMethod':
        """Create Robokassa payment method."""
        return PaymentMethod(value=PaymentMethodEnum.ROBOKASSA)
    
    @staticmethod
    def crypto_bot() -> 'PaymentMethod':
        """Create CryptoBot payment method."""
        return PaymentMethod(value=PaymentMethodEnum.CRYPTO_BOT)
    
    def is_telegram_stars(self) -> bool:
        """Check if method is Telegram Stars."""
        return self.value == PaymentMethodEnum.TELEGRAM_STARS
    
    def is_robokassa(self) -> bool:
        """Check if method is Robokassa."""
        return self.value == PaymentMethodEnum.ROBOKASSA
    
    def is_crypto_bot(self) -> bool:
        """Check if method is CryptoBot."""
        return self.value == PaymentMethodEnum.CRYPTO_BOT

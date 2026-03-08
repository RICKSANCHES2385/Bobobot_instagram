# 💎 Примеры Value Objects

## Базовый Value Object

```python
from abc import ABC
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class BaseValueObject(ABC):
    """Базовый класс для всех Value Objects.
    
    Характеристики:
    - Immutable (frozen=True)
    - Equality по значению
    - Валидация в __post_init__
    """
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))
```

## User Management Context

### UserId
```python
from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass(frozen=True)
class UserId(BaseValueObject):
    """Уникальный идентификатор пользователя."""
    value: UUID
    
    @staticmethod
    def generate() -> 'UserId':
        return UserId(uuid4())
    
    @staticmethod
    def from_string(value: str) -> 'UserId':
        return UserId(UUID(value))
    
    def __str__(self) -> str:
        return str(self.value)
```

### TelegramId
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TelegramId(BaseValueObject):
    """Telegram ID пользователя."""
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise InvalidTelegramIdException(
                f"Telegram ID must be positive, got {self.value}"
            )
    
    def __str__(self) -> str:
        return str(self.value)
```

### Username
```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class Username(BaseValueObject):
    """Username пользователя."""
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise InvalidUsernameException("Username cannot be empty")
        
        if len(self.value) > 32:
            raise InvalidUsernameException("Username too long (max 32 chars)")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', self.value):
            raise InvalidUsernameException(
                "Username can only contain letters, numbers and underscores"
            )
    
    def __str__(self) -> str:
        return self.value
```

### Profile
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Profile(BaseValueObject):
    """Профиль пользователя."""
    first_name: str
    last_name: Optional[str] = None
    
    def __post_init__(self):
        if not self.first_name:
            raise InvalidProfileException("First name is required")
        
        if len(self.first_name) > 64:
            raise InvalidProfileException("First name too long")
        
        if self.last_name and len(self.last_name) > 64:
            raise InvalidProfileException("Last name too long")
    
    def full_name(self) -> str:
        """Полное имя."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def __str__(self) -> str:
        return self.full_name()
```

### Language
```python
from dataclasses import dataclass
from enum import Enum

class LanguageCode(str, Enum):
    RUSSIAN = "ru"
    ENGLISH = "en"

@dataclass(frozen=True)
class Language(BaseValueObject):
    """Язык интерфейса."""
    code: LanguageCode
    
    @staticmethod
    def default() -> 'Language':
        return Language(LanguageCode.RUSSIAN)
    
    @staticmethod
    def from_string(code: str) -> 'Language':
        try:
            return Language(LanguageCode(code))
        except ValueError:
            return Language.default()
    
    def __str__(self) -> str:
        return self.code.value
```

## Subscription Context

### SubscriptionId
```python
from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass(frozen=True)
class SubscriptionId(BaseValueObject):
    """ID подписки."""
    value: UUID
    
    @staticmethod
    def generate() -> 'SubscriptionId':
        return SubscriptionId(uuid4())
    
    def __str__(self) -> str:
        return str(self.value)
```

### Period
```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True)
class Period(BaseValueObject):
    """Период подписки."""
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        if self.end_date <= self.start_date:
            raise InvalidPeriodException("End date must be after start date")
    
    @staticmethod
    def from_days(days: int) -> 'Period':
        """Создать период от текущей даты."""
        start = datetime.utcnow()
        end = start + timedelta(days=days)
        return Period(start, end)
    
    @staticmethod
    def from_duration(duration: 'Duration') -> 'Period':
        """Создать период из длительности."""
        return Period.from_days(duration.days)
    
    def is_expired(self) -> bool:
        """Проверка истечения."""
        return datetime.utcnow() > self.end_date
    
    def remaining_days(self) -> int:
        """Оставшиеся дни."""
        if self.is_expired():
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def extend(self, days: int) -> 'Period':
        """Продлить период."""
        new_end = self.end_date + timedelta(days=days)
        return Period(self.start_date, new_end)
```

### Duration
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Duration(BaseValueObject):
    """Длительность подписки."""
    days: int
    
    def __post_init__(self):
        if self.days <= 0:
            raise InvalidDurationException("Duration must be positive")
    
    @staticmethod
    def from_days(days: int) -> 'Duration':
        return Duration(days)
    
    def to_months(self) -> float:
        """Конвертация в месяцы."""
        return self.days / 30
    
    def __str__(self) -> str:
        if self.days == 7:
            return "7 дней"
        elif self.days == 30:
            return "1 месяц"
        elif self.days == 90:
            return "3 месяца"
        else:
            return f"{self.days} дней"
```

### Pricing
```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class Pricing(BaseValueObject):
    """Цены в разных валютах."""
    stars: Optional[int] = None
    rub: Optional[Decimal] = None
    ton: Optional[Decimal] = None
    usdt: Optional[Decimal] = None
    
    def __post_init__(self):
        # Хотя бы одна цена должна быть указана
        if not any([self.stars, self.rub, self.ton, self.usdt]):
            raise InvalidPricingException("At least one price must be specified")
        
        # Валидация положительных значений
        if self.stars is not None and self.stars <= 0:
            raise InvalidPricingException("Stars price must be positive")
        if self.rub is not None and self.rub <= 0:
            raise InvalidPricingException("RUB price must be positive")
        if self.ton is not None and self.ton <= 0:
            raise InvalidPricingException("TON price must be positive")
        if self.usdt is not None and self.usdt <= 0:
            raise InvalidPricingException("USDT price must be positive")
    
    def get_price(self, currency: 'Currency') -> Optional[Decimal]:
        """Получить цену в указанной валюте."""
        if currency.code == "XTR":
            return Decimal(self.stars) if self.stars else None
        elif currency.code == "RUB":
            return self.rub
        elif currency.code == "TON":
            return self.ton
        elif currency.code == "USDT":
            return self.usdt
        return None
```

## Payment Context

### Amount
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Amount(BaseValueObject):
    """Сумма платежа."""
    value: Decimal
    
    def __post_init__(self):
        if self.value <= 0:
            raise InvalidAmountException("Amount must be positive")
        
        # Максимум 2 знака после запятой
        if self.value.as_tuple().exponent < -2:
            raise InvalidAmountException("Amount can have max 2 decimal places")
    
    def add(self, other: 'Amount') -> 'Amount':
        """Сложение сумм."""
        return Amount(self.value + other.value)
    
    def subtract(self, other: 'Amount') -> 'Amount':
        """Вычитание сумм."""
        result = self.value - other.value
        if result < 0:
            raise InvalidAmountException("Result cannot be negative")
        return Amount(result)
    
    def multiply(self, factor: Decimal) -> 'Amount':
        """Умножение на коэффициент."""
        return Amount(self.value * factor)
    
    def __str__(self) -> str:
        return f"{self.value:.2f}"
```

### Currency
```python
from dataclasses import dataclass
from enum import Enum

class CurrencyCode(str, Enum):
    STARS = "XTR"
    RUBLES = "RUB"
    TON = "TON"
    USDT = "USDT"

@dataclass(frozen=True)
class Currency(BaseValueObject):
    """Валюта платежа."""
    code: CurrencyCode
    
    @staticmethod
    def stars() -> 'Currency':
        return Currency(CurrencyCode.STARS)
    
    @staticmethod
    def rubles() -> 'Currency':
        return Currency(CurrencyCode.RUBLES)
    
    @staticmethod
    def ton() -> 'Currency':
        return Currency(CurrencyCode.TON)
    
    @staticmethod
    def usdt() -> 'Currency':
        return Currency(CurrencyCode.USDT)
    
    def __str__(self) -> str:
        return self.code.value
```

### Money
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money(BaseValueObject):
    """Деньги (сумма + валюта)."""
    amount: Amount
    currency: Currency
    
    def add(self, other: 'Money') -> 'Money':
        """Сложение денег."""
        if self.currency != other.currency:
            raise CurrencyMismatchException(
                f"Cannot add {self.currency} and {other.currency}"
            )
        return Money(self.amount.add(other.amount), self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """Умножение на коэффициент."""
        return Money(self.amount.multiply(factor), self.currency)
    
    def calculate_commission(self, rate: Decimal) -> 'Money':
        """Расчет комиссии."""
        return self.multiply(rate)
    
    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
```

## Instagram Integration Context

### InstagramUsername
```python
import re
from dataclasses import dataclass

@dataclass(frozen=True)
class InstagramUsername(BaseValueObject):
    """Instagram username."""
    value: str
    
    def __post_init__(self):
        # Убрать @ если есть
        object.__setattr__(self, 'value', self.value.lstrip('@'))
        
        if not self.value:
            raise InvalidInstagramUsernameException("Username cannot be empty")
        
        if len(self.value) > 30:
            raise InvalidInstagramUsernameException("Username too long")
        
        if not re.match(r'^[a-zA-Z0-9._]+$', self.value):
            raise InvalidInstagramUsernameException(
                "Username can only contain letters, numbers, dots and underscores"
            )
    
    def with_at(self) -> str:
        """Username с @."""
        return f"@{self.value}"
    
    def __str__(self) -> str:
        return self.value
```

### ProfileStatistics
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ProfileStatistics(BaseValueObject):
    """Статистика профиля."""
    followers_count: int
    following_count: int
    posts_count: int
    
    def __post_init__(self):
        if self.followers_count < 0:
            raise InvalidStatisticsException("Followers count cannot be negative")
        if self.following_count < 0:
            raise InvalidStatisticsException("Following count cannot be negative")
        if self.posts_count < 0:
            raise InvalidStatisticsException("Posts count cannot be negative")
    
    def engagement_ratio(self) -> float:
        """Коэффициент вовлеченности."""
        if self.followers_count == 0:
            return 0.0
        return self.following_count / self.followers_count
    
    def format_followers(self) -> str:
        """Форматированное количество подписчиков."""
        if self.followers_count >= 1_000_000:
            return f"{self.followers_count / 1_000_000:.1f}M"
        elif self.followers_count >= 1_000:
            return f"{self.followers_count / 1_000:.1f}K"
        return str(self.followers_count)
```

## Referral Context

### CommissionRate
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class CommissionRate(BaseValueObject):
    """Ставка комиссии (в процентах)."""
    value: Decimal
    
    def __post_init__(self):
        if self.value < 0 or self.value > 100:
            raise InvalidCommissionRateException(
                "Commission rate must be between 0 and 100"
            )
    
    @staticmethod
    def default() -> 'CommissionRate':
        """Стандартная ставка 5%."""
        return CommissionRate(Decimal("5.0"))
    
    def as_decimal(self) -> Decimal:
        """Конвертация в десятичную дробь (5% -> 0.05)."""
        return self.value / 100
    
    def calculate(self, amount: Money) -> Money:
        """Расчет комиссии от суммы."""
        return amount.multiply(self.as_decimal())
    
    def __str__(self) -> str:
        return f"{self.value}%"
```

### Rewards
```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Rewards(BaseValueObject):
    """Награды реферала."""
    usdt: Decimal = Decimal("0")
    ton: Decimal = Decimal("0")
    stars: int = 0
    rub: Decimal = Decimal("0")
    
    def __post_init__(self):
        if self.usdt < 0 or self.ton < 0 or self.stars < 0 or self.rub < 0:
            raise InvalidRewardsException("Rewards cannot be negative")
    
    def add(self, other: 'Rewards') -> 'Rewards':
        """Сложение наград."""
        return Rewards(
            usdt=self.usdt + other.usdt,
            ton=self.ton + other.ton,
            stars=self.stars + other.stars,
            rub=self.rub + other.rub
        )
    
    def is_empty(self) -> bool:
        """Проверка на пустоту."""
        return all([
            self.usdt == 0,
            self.ton == 0,
            self.stars == 0,
            self.rub == 0
        ])
    
    def total_in_rub(self) -> Decimal:
        """Общая сумма в рублях (примерный расчет)."""
        # Примерные курсы
        usdt_rate = Decimal("90")  # 1 USDT = 90 RUB
        ton_rate = Decimal("180")  # 1 TON = 180 RUB
        stars_rate = Decimal("2")  # 1 Star = 2 RUB
        
        return (
            self.usdt * usdt_rate +
            self.ton * ton_rate +
            Decimal(self.stars) * stars_rate +
            self.rub
        )
```

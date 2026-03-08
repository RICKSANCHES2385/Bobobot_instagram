# 🏛️ Примеры Entities и Aggregates

## Базовые классы

### BaseEntity
```python
from abc import ABC
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BaseEntity(ABC):
    """Базовый класс для всех Entity.
    
    Характеристики:
    - Equality по ID
    - Mutable (в отличие от Value Objects)
    """
    id: Any
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
```

### AggregateRoot
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class AggregateRoot(BaseEntity):
    """Базовый класс для Aggregate Root.
    
    Характеристики:
    - Управляет domain events
    - Точка входа для изменений
    - Гарантирует консистентность
    """
    _domain_events: List['DomainEvent'] = field(default_factory=list, init=False, repr=False)
    
    def add_domain_event(self, event: 'DomainEvent') -> None:
        """Добавить доменное событие."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Очистить доменные события."""
        self._domain_events.clear()
    
    @property
    def domain_events(self) -> List['DomainEvent']:
        """Получить доменные события."""
        return self._domain_events.copy()
```

## User Management Context

### User Aggregate
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User(AggregateRoot):
    """Пользователь (Aggregate Root).
    
    Инварианты:
    - telegram_id уникален
    - username может быть None
    - language всегда установлен
    """
    telegram_id: TelegramId
    profile: Profile
    language: Language
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    username: Optional[Username] = None
    
    @staticmethod
    def register(
        telegram_id: TelegramId,
        profile: Profile,
        username: Optional[Username] = None,
        language: Optional[Language] = None
    ) -> 'User':
        """Регистрация нового пользователя (Factory Method)."""
        user_id = UserId.generate()
        user = User(
            id=user_id,
            telegram_id=telegram_id,
            profile=profile,
            username=username,
            language=language or Language.default()
        )
        
        # Publish domain event
        user.add_domain_event(UserRegistered(
            user_id=user_id,
            telegram_id=telegram_id,
            occurred_at=datetime.utcnow()
        ))
        
        return user
    
    def update_profile(self, profile: Profile) -> None:
        """Обновить профиль."""
        if self.profile == profile:
            return  # Нет изменений
        
        self.profile = profile
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(UserProfileUpdated(
            user_id=self.id,
            profile=profile,
            occurred_at=datetime.utcnow()
        ))
    
    def change_language(self, language: Language) -> None:
        """Изменить язык."""
        if self.language == language:
            return  # Нет изменений
        
        self.language = language
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(UserLanguageChanged(
            user_id=self.id,
            language=language,
            occurred_at=datetime.utcnow()
        ))
    
    def update_username(self, username: Optional[Username]) -> None:
        """Обновить username."""
        self.username = username
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"User({self.telegram_id}, {self.profile})"
```

## Subscription Context

### Subscription Aggregate
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class SubscriptionType(str, Enum):
    FREE = "free"
    PAID = "paid"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class Subscription(AggregateRoot):
    """Подписка (Aggregate Root).
    
    Инварианты:
    - Активная подписка не может быть истекшей
    - Период должен быть валидным
    - Нельзя продлить отмененную подписку
    """
    user_id: UserId
    subscription_type: SubscriptionType
    period: Period
    status: SubscriptionStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Валидация инвариантов."""
        self._validate_invariants()
    
    @staticmethod
    def activate(user_id: UserId, plan: 'SubscriptionPlan') -> 'Subscription':
        """Активировать подписку (Factory Method)."""
        subscription_id = SubscriptionId.generate()
        period = Period.from_duration(plan.duration)
        
        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            subscription_type=SubscriptionType.PAID,
            period=period,
            status=SubscriptionStatus.ACTIVE
        )
        
        # Publish domain event
        subscription.add_domain_event(SubscriptionActivated(
            subscription_id=subscription_id,
            user_id=user_id,
            plan_id=plan.id,
            period=period,
            occurred_at=datetime.utcnow()
        ))
        
        return subscription
    
    @staticmethod
    def create_trial(user_id: UserId) -> 'Subscription':
        """Создать пробную подписку на 7 дней."""
        subscription_id = SubscriptionId.generate()
        period = Period.from_days(7)
        
        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            subscription_type=SubscriptionType.PAID,
            period=period,
            status=SubscriptionStatus.ACTIVE
        )
        
        # Publish domain event
        subscription.add_domain_event(TrialSubscriptionCreated(
            subscription_id=subscription_id,
            user_id=user_id,
            period=period,
            occurred_at=datetime.utcnow()
        ))
        
        return subscription
    
    def extend(self, days: int) -> None:
        """Продлить подписку."""
        if self.status == SubscriptionStatus.CANCELLED:
            raise SubscriptionCancelledException("Cannot extend cancelled subscription")
        
        if self.is_expired():
            raise SubscriptionExpiredException("Cannot extend expired subscription")
        
        self.period = self.period.extend(days)
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(SubscriptionExtended(
            subscription_id=self.id,
            days=days,
            new_end_date=self.period.end_date,
            occurred_at=datetime.utcnow()
        ))
    
    def cancel(self) -> None:
        """Отменить подписку."""
        if self.status == SubscriptionStatus.CANCELLED:
            return  # Уже отменена
        
        self.status = SubscriptionStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(SubscriptionCancelled(
            subscription_id=self.id,
            occurred_at=datetime.utcnow()
        ))
    
    def check_expiration(self) -> None:
        """Проверить истечение подписки."""
        if self.status == SubscriptionStatus.ACTIVE and self.is_expired():
            self.status = SubscriptionStatus.EXPIRED
            self.updated_at = datetime.utcnow()
            
            # Publish domain event
            self.add_domain_event(SubscriptionExpired(
                subscription_id=self.id,
                user_id=self.user_id,
                occurred_at=datetime.utcnow()
            ))
    
    def is_expired(self) -> bool:
        """Проверка истечения."""
        return self.period.is_expired()
    
    def is_active(self) -> bool:
        """Проверка активности."""
        return self.status == SubscriptionStatus.ACTIVE and not self.is_expired()
    
    def remaining_days(self) -> int:
        """Оставшиеся дни."""
        return self.period.remaining_days()
    
    def _validate_invariants(self) -> None:
        """Валидация инвариантов."""
        if self.status == SubscriptionStatus.ACTIVE and self.is_expired():
            raise DomainException("Active subscription cannot be expired")
    
    def __str__(self) -> str:
        return f"Subscription({self.id}, {self.status}, expires: {self.period.end_date})"
```

### SubscriptionPlan Entity
```python
from dataclasses import dataclass

@dataclass
class SubscriptionPlan(BaseEntity):
    """Тарифный план подписки."""
    name: str
    duration: Duration
    pricing: Pricing
    is_active: bool = True
    
    def get_price(self, currency: Currency) -> Optional[Money]:
        """Получить цену в указанной валюте."""
        amount_value = self.pricing.get_price(currency)
        if amount_value is None:
            return None
        return Money(Amount(amount_value), currency)
    
    def deactivate(self) -> None:
        """Деактивировать план."""
        self.is_active = False
    
    def __str__(self) -> str:
        return f"SubscriptionPlan({self.name}, {self.duration})"
```

## Payment Context

### Payment Aggregate
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    TELEGRAM_STARS = "telegram_stars"
    ROBOKASSA = "robokassa"
    CRYPTO_BOT = "crypto_bot"

@dataclass
class Payment(AggregateRoot):
    """Платеж (Aggregate Root).
    
    Инварианты:
    - Завершенный платеж нельзя изменить
    - Возврат только для завершенных платежей
    - Сумма всегда положительная
    """
    user_id: UserId
    invoice_id: InvoiceId
    amount: Money
    payment_method: PaymentMethod
    status: PaymentStatus
    subscription_days: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    provider_payment_id: Optional[ProviderPaymentId] = None
    
    @staticmethod
    def create(
        user_id: UserId,
        invoice_id: InvoiceId,
        amount: Money,
        payment_method: PaymentMethod,
        subscription_days: int
    ) -> 'Payment':
        """Создать платеж (Factory Method)."""
        payment_id = PaymentId.generate()
        
        payment = Payment(
            id=payment_id,
            user_id=user_id,
            invoice_id=invoice_id,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            subscription_days=subscription_days
        )
        
        # Publish domain event
        payment.add_domain_event(PaymentCreated(
            payment_id=payment_id,
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            occurred_at=datetime.utcnow()
        ))
        
        return payment
    
    def process(self) -> None:
        """Начать обработку платежа."""
        if self.status != PaymentStatus.PENDING:
            raise InvalidPaymentStateException(
                f"Cannot process payment in {self.status} state"
            )
        
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(PaymentProcessing(
            payment_id=self.id,
            occurred_at=datetime.utcnow()
        ))
    
    def complete(self, provider_payment_id: Optional[ProviderPaymentId] = None) -> None:
        """Завершить платеж успешно."""
        if self.status == PaymentStatus.COMPLETED:
            raise PaymentAlreadyProcessedException("Payment already completed")
        
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise InvalidPaymentStateException(
                f"Cannot complete payment in {self.status} state"
            )
        
        self.status = PaymentStatus.COMPLETED
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.provider_payment_id = provider_payment_id
        
        # Publish domain event
        self.add_domain_event(PaymentCompleted(
            payment_id=self.id,
            user_id=self.user_id,
            amount=self.amount,
            subscription_days=self.subscription_days,
            occurred_at=datetime.utcnow()
        ))
    
    def fail(self, reason: str) -> None:
        """Провалить платеж."""
        if self.status == PaymentStatus.COMPLETED:
            raise PaymentAlreadyProcessedException("Cannot fail completed payment")
        
        self.status = PaymentStatus.FAILED
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(PaymentFailed(
            payment_id=self.id,
            reason=reason,
            occurred_at=datetime.utcnow()
        ))
    
    def refund(self) -> None:
        """Вернуть деньги."""
        if not self.can_be_refunded():
            raise CannotRefundPaymentException(
                f"Cannot refund payment in {self.status} state"
            )
        
        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(PaymentRefunded(
            payment_id=self.id,
            user_id=self.user_id,
            amount=self.amount,
            occurred_at=datetime.utcnow()
        ))
    
    def can_be_refunded(self) -> bool:
        """Можно ли вернуть деньги."""
        return self.status == PaymentStatus.COMPLETED
    
    def __str__(self) -> str:
        return f"Payment({self.id}, {self.amount}, {self.status})"
```

### Invoice Entity
```python
from dataclasses import dataclass

@dataclass
class Invoice(BaseEntity):
    """Счет на оплату."""
    payment_id: PaymentId
    amount: Money
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __str__(self) -> str:
        return f"Invoice({self.id}, {self.amount})"
```

## Content Tracking Context

### ContentTracking Aggregate
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Set

class ContentType(str, Enum):
    STORY = "story"
    POST = "post"
    REEL = "reel"

class CheckInterval(int, Enum):
    ONE_HOUR = 1
    SIX_HOURS = 6
    TWELVE_HOURS = 12
    TWENTY_FOUR_HOURS = 24

class TrackingStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class ContentTracking(AggregateRoot):
    """Отслеживание контента (Aggregate Root).
    
    Инварианты:
    - Хотя бы один тип контента должен отслеживаться
    - Интервал проверки должен быть валидным
    - Нельзя активировать отмененное отслеживание
    """
    user_id: UserId
    target_profile: TargetProfile
    tracked_types: Set[ContentType]
    check_interval: CheckInterval
    status: TrackingStatus
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_check_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Валидация инвариантов."""
        if not self.tracked_types:
            raise InvalidTrackingException("At least one content type must be tracked")
    
    @staticmethod
    def activate(
        user_id: UserId,
        target_profile: TargetProfile,
        tracked_types: Set[ContentType],
        check_interval: CheckInterval
    ) -> 'ContentTracking':
        """Активировать отслеживание (Factory Method)."""
        tracking_id = TrackingId.generate()
        
        tracking = ContentTracking(
            id=tracking_id,
            user_id=user_id,
            target_profile=target_profile,
            tracked_types=tracked_types,
            check_interval=check_interval,
            status=TrackingStatus.ACTIVE
        )
        
        # Publish domain event
        tracking.add_domain_event(TrackingActivated(
            tracking_id=tracking_id,
            user_id=user_id,
            target_profile=target_profile,
            tracked_types=tracked_types,
            occurred_at=datetime.utcnow()
        ))
        
        return tracking
    
    def deactivate(self) -> None:
        """Деактивировать отслеживание."""
        if self.status == TrackingStatus.CANCELLED:
            return  # Уже отменено
        
        self.status = TrackingStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(TrackingDeactivated(
            tracking_id=self.id,
            occurred_at=datetime.utcnow()
        ))
    
    def pause(self) -> None:
        """Приостановить отслеживание."""
        if self.status != TrackingStatus.ACTIVE:
            return
        
        self.status = TrackingStatus.PAUSED
        self.updated_at = datetime.utcnow()
    
    def resume(self) -> None:
        """Возобновить отслеживание."""
        if self.status != TrackingStatus.PAUSED:
            return
        
        self.status = TrackingStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def update_settings(
        self,
        tracked_types: Set[ContentType],
        check_interval: CheckInterval
    ) -> None:
        """Обновить настройки."""
        if not tracked_types:
            raise InvalidTrackingException("At least one content type must be tracked")
        
        self.tracked_types = tracked_types
        self.check_interval = check_interval
        self.updated_at = datetime.utcnow()
    
    def should_check(self) -> bool:
        """Нужна ли проверка."""
        if self.status != TrackingStatus.ACTIVE:
            return False
        
        if self.last_check_at is None:
            return True
        
        time_since_check = datetime.utcnow() - self.last_check_at
        return time_since_check.total_seconds() >= self.check_interval.value * 3600
    
    def mark_checked(self) -> None:
        """Отметить проверку."""
        self.last_check_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"ContentTracking({self.target_profile}, {self.tracked_types})"
```

### TrackedContent Entity
```python
from dataclasses import dataclass

@dataclass
class TrackedContent(BaseEntity):
    """Отслеженный контент."""
    tracking_id: TrackingId
    content_type: ContentType
    content_id: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    
    def __str__(self) -> str:
        return f"TrackedContent({self.content_type}, {self.content_id})"
```

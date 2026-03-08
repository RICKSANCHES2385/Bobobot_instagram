# 🏗️ ЭТАП 3: SUBSCRIPTION MANAGEMENT CONTEXT - ДЕТАЛЬНЫЙ ПЛАН

## 📋 ОГЛАВЛЕНИЕ
1. [Обзор этапа](#обзор-этапа)
2. [Цели и задачи](#цели-и-задачи)
3. [Domain Layer](#domain-layer)
4. [Application Layer](#application-layer)
5. [Infrastructure Layer](#infrastructure-layer)
6. [Тестирование](#тестирование)
7. [Чеклист выполнения](#чеклист-выполнения)

---

## ОБЗОР ЭТАПА

**Длительность:** 2-3 дня  
**Приоритет:** ВЫСОКИЙ  
**Зависимости:** Этап 2 (User Management) ✅

### Что будет создано:
- Subscription Aggregate с Value Objects
- Use Cases для управления подписками
- Repository интерфейс и реализация
- Domain Events
- 100% покрытие тестами

---

## ЦЕЛИ И ЗАДАЧИ

### Главная цель:
Создать Subscription Management bounded context - управление подписками пользователей с различными тарифами.

### Бизнес-требования:
- Поддержка 3 типов подписок: FREE, BASIC, PREMIUM
- Автоматическая проверка истечения подписки
- Возможность продления подписки
- Отмена подписки
- История подписок пользователя

### Задачи:

#### 1. Domain Layer (1 день)
- [ ] Value Objects (SubscriptionId, SubscriptionType, SubscriptionStatus, SubscriptionPeriod)
- [ ] Subscription Aggregate Root
- [ ] Domain Events
- [ ] Repository Interface
- [ ] Domain Exceptions

#### 2. Application Layer (0.5 дня)
- [ ] CreateSubscriptionUseCase
- [ ] RenewSubscriptionUseCase
- [ ] CancelSubscriptionUseCase
- [ ] GetSubscriptionUseCase
- [ ] CheckSubscriptionStatusUseCase
- [ ] DTOs

#### 3. Infrastructure Layer (0.5 дня)
- [ ] SQLAlchemy Models
- [ ] Repository Implementation
- [ ] Migrations

#### 4. Тестирование (1 день)
- [ ] Unit тесты Domain Layer (100%)
- [ ] Unit тесты Application Layer
- [ ] Integration тесты Repository

---

## DOMAIN LAYER

### 1. Value Objects

#### SubscriptionId
**Файл:** `src/domain/subscription/value_objects/subscription_id.py`

```python
"""Subscription ID Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.identifier import Identifier


@dataclass(frozen=True)
class SubscriptionId(Identifier[int]):
    """Subscription identifier."""
    pass
```

**Тесты:**
- [ ] test_subscription_id_creation
- [ ] test_subscription_id_equality
- [ ] test_subscription_id_hash

---

#### SubscriptionType
**Файл:** `src/domain/subscription/value_objects/subscription_type.py`

```python
"""Subscription Type Value Object."""
from dataclasses import dataclass
from enum import Enum
from src.domain.shared.value_objects.base import BaseValueObject


class SubscriptionTypeEnum(str, Enum):
    """Subscription type enum."""
    FREE = "FREE"
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"


@dataclass(frozen=True)
class SubscriptionType(BaseValueObject):
    """Subscription type."""
    
    type: SubscriptionTypeEnum
    
    def _validate(self) -> None:
        """Validate subscription type."""
        if not isinstance(self.type, SubscriptionTypeEnum):
            raise ValueError(f"Invalid subscription type: {self.type}")
    
    @classmethod
    def free(cls) -> 'SubscriptionType':
        """Get FREE subscription type."""
        return cls(type=SubscriptionTypeEnum.FREE)
    
    @classmethod
    def basic(cls) -> 'SubscriptionType':
        """Get BASIC subscription type."""
        return cls(type=SubscriptionTypeEnum.BASIC)
    
    @classmethod
    def premium(cls) -> 'SubscriptionType':
        """Get PREMIUM subscription type."""
        return cls(type=SubscriptionTypeEnum.PREMIUM)
    
    def is_free(self) -> bool:
        """Check if subscription is free."""
        return self.type == SubscriptionTypeEnum.FREE
    
    def is_paid(self) -> bool:
        """Check if subscription is paid."""
        return self.type in (SubscriptionTypeEnum.BASIC, SubscriptionTypeEnum.PREMIUM)
```

**Тесты:**
- [ ] test_subscription_type_creation
- [ ] test_subscription_type_free
- [ ] test_subscription_type_basic
- [ ] test_subscription_type_premium
- [ ] test_subscription_type_is_free
- [ ] test_subscription_type_is_paid
- [ ] test_subscription_type_validates_type

---

#### SubscriptionStatus
**Файл:** `src/domain/subscription/value_objects/subscription_status.py`

```python
"""Subscription Status Value Object."""
from dataclasses import dataclass
from enum import Enum
from src.domain.shared.value_objects.base import BaseValueObject


class SubscriptionStatusEnum(str, Enum):
    """Subscription status enum."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class SubscriptionStatus(BaseValueObject):
    """Subscription status."""
    
    status: SubscriptionStatusEnum
    
    def _validate(self) -> None:
        """Validate subscription status."""
        if not isinstance(self.status, SubscriptionStatusEnum):
            raise ValueError(f"Invalid subscription status: {self.status}")
    
    @classmethod
    def active(cls) -> 'SubscriptionStatus':
        """Get ACTIVE status."""
        return cls(status=SubscriptionStatusEnum.ACTIVE)
    
    @classmethod
    def expired(cls) -> 'SubscriptionStatus':
        """Get EXPIRED status."""
        return cls(status=SubscriptionStatusEnum.EXPIRED)
    
    @classmethod
    def cancelled(cls) -> 'SubscriptionStatus':
        """Get CANCELLED status."""
        return cls(status=SubscriptionStatusEnum.CANCELLED)
    
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == SubscriptionStatusEnum.ACTIVE
```

**Тесты:**
- [ ] test_subscription_status_creation
- [ ] test_subscription_status_active
- [ ] test_subscription_status_expired
- [ ] test_subscription_status_cancelled
- [ ] test_subscription_status_is_active
- [ ] test_subscription_status_validates_status

---

#### SubscriptionPeriod
**Файл:** `src/domain/subscription/value_objects/subscription_period.py`

```python
"""Subscription Period Value Object."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class SubscriptionPeriod(BaseValueObject):
    """Subscription period with start and end dates."""
    
    start_date: datetime
    end_date: datetime
    
    def _validate(self) -> None:
        """Validate subscription period."""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
    
    @classmethod
    def from_days(cls, days: int, start_date: datetime | None = None) -> 'SubscriptionPeriod':
        """Create period from number of days."""
        if days <= 0:
            raise ValueError("Days must be positive")
        
        start = start_date or datetime.utcnow()
        end = start + timedelta(days=days)
        return cls(start_date=start, end_date=end)
    
    def is_expired(self) -> bool:
        """Check if period is expired."""
        return datetime.utcnow() > self.end_date
    
    def days_remaining(self) -> int:
        """Get remaining days."""
        if self.is_expired():
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)
    
    def extend(self, days: int) -> 'SubscriptionPeriod':
        """Extend period by days."""
        if days <= 0:
            raise ValueError("Days must be positive")
        
        new_end = self.end_date + timedelta(days=days)
        return SubscriptionPeriod(start_date=self.start_date, end_date=new_end)
```

**Тесты:**
- [ ] test_subscription_period_creation
- [ ] test_subscription_period_validates_dates
- [ ] test_subscription_period_from_days
- [ ] test_subscription_period_from_days_validates_positive
- [ ] test_subscription_period_is_expired
- [ ] test_subscription_period_days_remaining
- [ ] test_subscription_period_extend

---

### 2. Subscription Aggregate

**Файл:** `src/domain/subscription/aggregates/subscription.py`

```python
"""Subscription Aggregate Root."""
from dataclasses import dataclass
from datetime import datetime
from src.domain.shared.entities.base import AggregateRoot
from ..value_objects.subscription_id import SubscriptionId
from ..value_objects.subscription_type import SubscriptionType
from ..value_objects.subscription_status import SubscriptionStatus
from ..value_objects.subscription_period import SubscriptionPeriod
from src.domain.user_management.value_objects.user_id import UserId
from ..events.subscription_events import (
    SubscriptionCreated,
    SubscriptionRenewed,
    SubscriptionCancelled,
    SubscriptionExpired
)


@dataclass(eq=False)
class Subscription(AggregateRoot):
    """Subscription aggregate root.
    
    Represents a user subscription with type, status, and period.
    """
    
    user_id: UserId = None  # type: ignore
    subscription_type: SubscriptionType = None  # type: ignore
    status: SubscriptionStatus = None  # type: ignore
    period: SubscriptionPeriod = None  # type: ignore
    
    @staticmethod
    def create(
        subscription_id: SubscriptionId,
        user_id: UserId,
        subscription_type: SubscriptionType,
        period: SubscriptionPeriod
    ) -> 'Subscription':
        """Create a new subscription.
        
        Args:
            subscription_id: Subscription ID.
            user_id: User ID.
            subscription_type: Subscription type.
            period: Subscription period.
            
        Returns:
            New Subscription instance.
        """
        subscription = Subscription(
            id=subscription_id,
            user_id=user_id,
            subscription_type=subscription_type,
            status=SubscriptionStatus.active(),
            period=period
        )
        
        subscription.add_domain_event(
            SubscriptionCreated(
                subscription_id=subscription_id.value,
                user_id=user_id.value,
                subscription_type=subscription_type.type.value,
                end_date=period.end_date.isoformat()
            )
        )
        
        return subscription
    
    def renew(self, days: int) -> None:
        """Renew subscription by extending period.
        
        Args:
            days: Number of days to extend.
        """
        if not self.status.is_active():
            raise ValueError("Cannot renew inactive subscription")
        
        old_end_date = self.period.end_date
        self.period = self.period.extend(days)
        self._touch()
        
        self.add_domain_event(
            SubscriptionRenewed(
                subscription_id=self.id.value,
                user_id=self.user_id.value,
                old_end_date=old_end_date.isoformat(),
                new_end_date=self.period.end_date.isoformat(),
                days_added=days
            )
        )
    
    def cancel(self) -> None:
        """Cancel subscription."""
        if not self.status.is_active():
            raise ValueError("Cannot cancel inactive subscription")
        
        object.__setattr__(self, 'status', SubscriptionStatus.cancelled())
        self._touch()
        
        self.add_domain_event(
            SubscriptionCancelled(
                subscription_id=self.id.value,
                user_id=self.user_id.value,
                cancelled_at=datetime.utcnow().isoformat()
            )
        )
    
    def check_expiration(self) -> None:
        """Check and update expiration status."""
        if self.status.is_active() and self.period.is_expired():
            object.__setattr__(self, 'status', SubscriptionStatus.expired())
            self._touch()
            
            self.add_domain_event(
                SubscriptionExpired(
                    subscription_id=self.id.value,
                    user_id=self.user_id.value,
                    expired_at=self.period.end_date.isoformat()
                )
            )
    
    def is_active(self) -> bool:
        """Check if subscription is active and not expired."""
        self.check_expiration()
        return self.status.is_active()
    
    def days_remaining(self) -> int:
        """Get remaining days."""
        if not self.is_active():
            return 0
        return self.period.days_remaining()
```

**Тесты:**
- [ ] test_subscription_create
- [ ] test_subscription_renew
- [ ] test_subscription_renew_inactive_raises
- [ ] test_subscription_cancel
- [ ] test_subscription_cancel_inactive_raises
- [ ] test_subscription_check_expiration
- [ ] test_subscription_is_active
- [ ] test_subscription_days_remaining
- [ ] test_subscription_create_emits_event
- [ ] test_subscription_renew_emits_event
- [ ] test_subscription_cancel_emits_event
- [ ] test_subscription_expire_emits_event

---

### 3. Domain Events

**Файл:** `src/domain/subscription/events/subscription_events.py`

```python
"""Subscription Domain Events."""
from dataclasses import dataclass
from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class SubscriptionCreated(DomainEvent):
    """Subscription created event."""
    subscription_id: int = 0
    user_id: int = 0
    subscription_type: str = ""
    end_date: str = ""


@dataclass(frozen=True)
class SubscriptionRenewed(DomainEvent):
    """Subscription renewed event."""
    subscription_id: int = 0
    user_id: int = 0
    old_end_date: str = ""
    new_end_date: str = ""
    days_added: int = 0


@dataclass(frozen=True)
class SubscriptionCancelled(DomainEvent):
    """Subscription cancelled event."""
    subscription_id: int = 0
    user_id: int = 0
    cancelled_at: str = ""


@dataclass(frozen=True)
class SubscriptionExpired(DomainEvent):
    """Subscription expired event."""
    subscription_id: int = 0
    user_id: int = 0
    expired_at: str = ""
```

**Тесты:**
- [ ] test_subscription_created_event
- [ ] test_subscription_renewed_event
- [ ] test_subscription_cancelled_event
- [ ] test_subscription_expired_event

---

### 4. Repository Interface

**Файл:** `src/domain/subscription/repositories/subscription_repository.py`

```python
"""Subscription Repository Interface."""
from abc import ABC, abstractmethod
from typing import Optional
from ..aggregates.subscription import Subscription
from ..value_objects.subscription_id import SubscriptionId
from src.domain.user_management.value_objects.user_id import UserId


class SubscriptionRepository(ABC):
    """Subscription repository interface."""
    
    @abstractmethod
    async def save(self, subscription: Subscription) -> None:
        """Save subscription."""
        pass
    
    @abstractmethod
    async def get_by_id(self, subscription_id: SubscriptionId) -> Optional[Subscription]:
        """Get subscription by ID."""
        pass
    
    @abstractmethod
    async def get_active_by_user_id(self, user_id: UserId) -> Optional[Subscription]:
        """Get active subscription for user."""
        pass
    
    @abstractmethod
    async def get_all_by_user_id(self, user_id: UserId) -> list[Subscription]:
        """Get all subscriptions for user."""
        pass
    
    @abstractmethod
    async def delete(self, subscription_id: SubscriptionId) -> None:
        """Delete subscription."""
        pass
```

---

### 5. Domain Exceptions

**Файл:** `src/domain/subscription/exceptions.py`

```python
"""Subscription Domain Exceptions."""
from src.domain.shared.exceptions.base import DomainException


class SubscriptionNotFoundException(DomainException):
    """Subscription not found."""
    
    def __init__(self, identifier: str):
        super().__init__(
            message=f"Subscription not found: {identifier}",
            code="SUBSCRIPTION_NOT_FOUND"
        )


class SubscriptionAlreadyExistsException(DomainException):
    """Active subscription already exists."""
    
    def __init__(self, user_id: int):
        super().__init__(
            message=f"Active subscription already exists for user {user_id}",
            code="SUBSCRIPTION_ALREADY_EXISTS"
        )


class InvalidSubscriptionOperationException(DomainException):
    """Invalid subscription operation."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="INVALID_SUBSCRIPTION_OPERATION"
        )
```

**Тесты:**
- [ ] test_subscription_not_found_exception
- [ ] test_subscription_already_exists_exception
- [ ] test_invalid_subscription_operation_exception

---

## APPLICATION LAYER

### 1. DTOs

**Файл:** `src/application/subscription/dtos.py`

```python
"""Subscription DTOs."""
from dataclasses import dataclass


@dataclass
class CreateSubscriptionCommand:
    """Create subscription command."""
    user_id: int
    subscription_type: str
    days: int


@dataclass
class RenewSubscriptionCommand:
    """Renew subscription command."""
    user_id: int
    days: int


@dataclass
class CancelSubscriptionCommand:
    """Cancel subscription command."""
    user_id: int


@dataclass
class SubscriptionDTO:
    """Subscription data transfer object."""
    id: int
    user_id: int
    subscription_type: str
    status: str
    start_date: str
    end_date: str
    days_remaining: int
    is_active: bool
    created_at: str
    updated_at: str
```

---

### 2. Use Cases

#### CreateSubscriptionUseCase
**Файл:** `src/application/subscription/use_cases/create_subscription.py`

```python
"""Create Subscription Use Case."""
from datetime import datetime
from ..dtos import CreateSubscriptionCommand, SubscriptionDTO
from ...shared.use_case import UseCase
from ....domain.subscription.aggregates.subscription import Subscription
from ....domain.subscription.value_objects.subscription_id import SubscriptionId
from ....domain.subscription.value_objects.subscription_type import (
    SubscriptionType,
    SubscriptionTypeEnum
)
from ....domain.subscription.value_objects.subscription_period import SubscriptionPeriod
from ....domain.subscription.repositories.subscription_repository import SubscriptionRepository
from ....domain.subscription.exceptions import SubscriptionAlreadyExistsException
from ....domain.user_management.value_objects.user_id import UserId


class CreateSubscriptionUseCase(UseCase[CreateSubscriptionCommand, SubscriptionDTO]):
    """Create a new subscription."""
    
    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repository = subscription_repository
    
    async def execute(self, command: CreateSubscriptionCommand) -> SubscriptionDTO:
        """Execute use case."""
        user_id = UserId(value=command.user_id)
        
        # Check if active subscription exists
        existing = await self.subscription_repository.get_active_by_user_id(user_id)
        if existing:
            raise SubscriptionAlreadyExistsException(user_id=command.user_id)
        
        # Create subscription
        subscription_type = SubscriptionType(type=SubscriptionTypeEnum(command.subscription_type))
        period = SubscriptionPeriod.from_days(days=command.days)
        
        subscription = Subscription.create(
            subscription_id=SubscriptionId(value=0),
            user_id=user_id,
            subscription_type=subscription_type,
            period=period
        )
        
        await self.subscription_repository.save(subscription)
        
        return SubscriptionDTO(
            id=subscription.id.value,
            user_id=subscription.user_id.value,
            subscription_type=subscription.subscription_type.type.value,
            status=subscription.status.status.value,
            start_date=subscription.period.start_date.isoformat(),
            end_date=subscription.period.end_date.isoformat(),
            days_remaining=subscription.days_remaining(),
            is_active=subscription.is_active(),
            created_at=subscription.created_at.isoformat(),
            updated_at=subscription.updated_at.isoformat()
        )
```

**Тесты:**
- [ ] test_create_subscription_success
- [ ] test_create_subscription_already_exists_raises
- [ ] test_create_subscription_invalid_type_raises
- [ ] test_create_subscription_invalid_days_raises

---

## ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### День 1: Domain Layer ✅
- [ ] SubscriptionId + тесты (3)
- [ ] SubscriptionType + тесты (7)
- [ ] SubscriptionStatus + тесты (6)
- [ ] SubscriptionPeriod + тесты (7)
- [ ] Subscription Aggregate + тесты (12)
- [ ] Domain Events + тесты (4)
- [ ] Domain Exceptions + тесты (3)
- [ ] Repository Interface

### День 2: Application + Infrastructure
- [ ] DTOs
- [ ] CreateSubscriptionUseCase + тесты (4)
- [ ] RenewSubscriptionUseCase + тесты (3)
- [ ] CancelSubscriptionUseCase + тесты (3)
- [ ] GetSubscriptionUseCase + тесты (2)
- [ ] CheckSubscriptionStatusUseCase + тесты (2)
- [ ] SQLAlchemy Models
- [ ] Repository Implementation + тесты (8)
- [ ] Alembic Migration

---

**Дата создания:** 2026-03-08  
**Автор:** Kiro AI Assistant  
**Статус:** План готов ✅  
**Следующий этап:** ЭТАП_4_PAYMENT_ПЛАН.md

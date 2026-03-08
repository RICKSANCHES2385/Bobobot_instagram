# 🏗️ ЭТАП 1: SHARED KERNEL - ДЕТАЛЬНЫЙ ПЛАН

## 📋 ОГЛАВЛЕНИЕ
1. [Обзор этапа](#обзор-этапа)
2. [Цели и задачи](#цели-и-задачи)
3. [Базовые абстракции](#базовые-абстракции)
4. [Общие Value Objects](#общие-value-objects)
5. [Event Dispatcher](#event-dispatcher)
6. [Specification Pattern](#specification-pattern)
7. [Тестирование](#тестирование)
8. [Чеклист выполнения](#чеклист-выполнения)

---

## ОБЗОР ЭТАПА

**Длительность:** 3-4 дня  
**Приоритет:** КРИТИЧЕСКИЙ (блокирует все остальные этапы)  
**Зависимости:** Нет (первый этап)

### Что будет создано:
- Базовые абстракции для всех слоев
- Общие Value Objects
- Event Dispatcher для доменных событий
- Specification Pattern для бизнес-правил
- 100% покрытие тестами

---

## ЦЕЛИ И ЗАДАЧИ

### Главная цель:
Создать фундамент для всей DDD архитектуры - базовые классы и паттерны, которые будут использоваться во всех bounded contexts.

### Задачи:

#### 1. Базовые абстракции (1 день)
- [ ] BaseValueObject - базовый класс для Value Objects
- [ ] BaseEntity - базовый класс для Entities
- [ ] AggregateRoot - базовый класс для Aggregate Roots
- [ ] DomainEvent - базовый класс для доменных событий
- [ ] DomainException - базовый класс для доменных исключений

#### 2. Общие Value Objects (1 день)
- [ ] Identifier - базовый класс для ID
- [ ] Money - деньги с валютой
- [ ] DateRange - диапазон дат
- [ ] Email - email с валидацией
- [ ] PhoneNumber - телефон с валидацией

#### 3. Event Dispatcher (0.5 дня)
- [ ] EventDispatcher - публикация событий
- [ ] EventHandler - интерфейс обработчика
- [ ] In-memory event bus

#### 4. Specification Pattern (0.5 дня)
- [ ] Specification - базовый класс
- [ ] AndSpecification, OrSpecification, NotSpecification
- [ ] Примеры использования

#### 5. Тестирование (1 день)
- [ ] Unit тесты для всех компонентов
- [ ] 100% покрытие
- [ ] Документация

---

## БАЗОВЫЕ АБСТРАКЦИИ

### 1. BaseValueObject

**Файл:** `src/domain/shared/value_objects/base.py`

**Требования:**
- Immutable (frozen dataclass)
- Equality по значению
- Hash support
- Валидация в __post_init__

**Пример:**
```python
from dataclasses import dataclass
from abc import ABC

@dataclass(frozen=True)
class BaseValueObject(ABC):
    """Base class for all Value Objects."""
    
    def __post_init__(self):
        """Validate value object after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Override in subclasses to add validation."""
        pass
```

**Тесты:**
- [ ] test_value_object_is_immutable
- [ ] test_value_object_equality_by_value
- [ ] test_value_object_hash
- [ ] test_value_object_validation

---

### 2. BaseEntity

**Файл:** `src/domain/shared/entities/base.py`

**Требования:**
- Mutable
- Equality по ID
- Hash по ID
- created_at, updated_at timestamps

**Пример:**
```python
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC
from typing import Any

@dataclass
class BaseEntity(ABC):
    """Base class for all Entities."""
    
    id: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __eq__(self, other: object) -> bool:
        """Equality by ID."""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash by ID."""
        return hash(self.id)
    
    def _touch(self) -> None:
        """Update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
```

**Тесты:**
- [ ] test_entity_equality_by_id
- [ ] test_entity_hash_by_id
- [ ] test_entity_timestamps
- [ ] test_entity_touch_updates_timestamp

---

### 3. AggregateRoot

**Файл:** `src/domain/shared/entities/base.py`

**Требования:**
- Наследует BaseEntity
- Управление доменными событиями
- add_domain_event(), clear_domain_events()

**Пример:**
```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class AggregateRoot(BaseEntity):
    """Base class for Aggregate Roots."""
    
    _domain_events: List['DomainEvent'] = field(default_factory=list, init=False, repr=False)
    
    def add_domain_event(self, event: 'DomainEvent') -> None:
        """Add domain event."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear domain events."""
        self._domain_events.clear()
    
    @property
    def domain_events(self) -> List['DomainEvent']:
        """Get domain events."""
        return self._domain_events.copy()
```

**Тесты:**
- [ ] test_aggregate_can_add_domain_events
- [ ] test_aggregate_can_clear_domain_events
- [ ] test_aggregate_domain_events_are_copied

---

### 4. DomainEvent

**Файл:** `src/domain/shared/events/base.py`

**Требования:**
- Immutable
- occurred_at timestamp
- event_id UUID

**Пример:**
```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass(frozen=True)
class DomainEvent:
    """Base class for Domain Events."""
    
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
```

**Тесты:**
- [ ] test_domain_event_is_immutable
- [ ] test_domain_event_has_id
- [ ] test_domain_event_has_timestamp

---

### 5. DomainException

**Файл:** `src/domain/shared/exceptions/base.py`

**Требования:**
- Наследует Exception
- message, code

**Пример:**
```python
class DomainException(Exception):
    """Base class for Domain Exceptions."""
    
    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)
```

**Тесты:**
- [ ] test_domain_exception_has_message
- [ ] test_domain_exception_has_code

---

## ОБЩИЕ VALUE OBJECTS

### 1. Identifier

**Файл:** `src/domain/shared/value_objects/identifier.py`

**Требования:**
- Generic base class для всех ID
- Валидация типа
- Конвертация в int/str/UUID

**Пример:**
```python
from dataclasses import dataclass
from typing import TypeVar, Generic
from .base import BaseValueObject

T = TypeVar('T', int, str, UUID)

@dataclass(frozen=True)
class Identifier(BaseValueObject, Generic[T]):
    """Base class for identifiers."""
    
    value: T
    
    def _validate(self) -> None:
        if self.value is None:
            raise ValueError("Identifier value cannot be None")
```

**Тесты:**
- [ ] test_identifier_with_int
- [ ] test_identifier_with_str
- [ ] test_identifier_with_uuid
- [ ] test_identifier_validates_none

---

### 2. Money

**Файл:** `src/domain/shared/value_objects/money.py`

**Требования:**
- amount (Decimal)
- currency (Currency enum)
- Операции: add, subtract, multiply
- Валидация: amount >= 0

**Пример:**
```python
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from .base import BaseValueObject

class Currency(str, Enum):
    XTR = "XTR"  # Telegram Stars
    RUB = "RUB"
    TON = "TON"
    USDT = "USDT"

@dataclass(frozen=True)
class Money(BaseValueObject):
    """Money value object."""
    
    amount: Decimal
    currency: Currency
    
    def _validate(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
```

**Тесты:**
- [ ] test_money_creation
- [ ] test_money_validates_negative
- [ ] test_money_add_same_currency
- [ ] test_money_add_different_currency_raises
- [ ] test_money_subtract
- [ ] test_money_multiply

---

### 3. DateRange

**Файл:** `src/domain/shared/value_objects/date_range.py`

**Требования:**
- start_date, end_date
- Валидация: start <= end
- contains(), overlaps(), duration()

**Пример:**
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from .base import BaseValueObject

@dataclass(frozen=True)
class DateRange(BaseValueObject):
    """Date range value object."""
    
    start_date: datetime
    end_date: datetime
    
    def _validate(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
    
    def contains(self, date: datetime) -> bool:
        return self.start_date <= date <= self.end_date
    
    def overlaps(self, other: 'DateRange') -> bool:
        return self.start_date <= other.end_date and other.start_date <= self.end_date
    
    def duration(self) -> timedelta:
        return self.end_date - self.start_date
```

**Тесты:**
- [ ] test_date_range_creation
- [ ] test_date_range_validates_order
- [ ] test_date_range_contains
- [ ] test_date_range_overlaps
- [ ] test_date_range_duration

---

## EVENT DISPATCHER

**Файл:** `src/domain/shared/events/event_dispatcher.py`

**Требования:**
- Регистрация обработчиков
- Публикация событий
- In-memory реализация

**Пример:**
```python
from typing import Dict, List, Type, Callable
from .base import DomainEvent

class EventDispatcher:
    """Event dispatcher for domain events."""
    
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
    
    def register(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def dispatch(self, event: DomainEvent) -> None:
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

**Тесты:**
- [ ] test_event_dispatcher_register
- [ ] test_event_dispatcher_dispatch
- [ ] test_event_dispatcher_multiple_handlers

---

## SPECIFICATION PATTERN

**Файл:** `src/domain/shared/specifications/base.py`

**Требования:**
- is_satisfied_by()
- and_(), or_(), not_()
- Композиция спецификаций

**Пример:**
```python
from abc import ABC, abstractmethod
from typing import Any

class Specification(ABC):
    """Base class for specifications."""
    
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'Specification':
        return OrSpecification(self, other)
    
    def not_(self) -> 'Specification':
        return NotSpecification(self)

class AndSpecification(Specification):
    def __init__(self, left: Specification, right: Specification):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: Any) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)
```

**Тесты:**
- [ ] test_specification_and
- [ ] test_specification_or
- [ ] test_specification_not
- [ ] test_specification_composition

---

## ТЕСТИРОВАНИЕ

### Структура тестов:
```
tests/
└── unit/
    └── domain/
        └── shared/
            ├── test_base_value_object.py
            ├── test_base_entity.py
            ├── test_aggregate_root.py
            ├── test_domain_event.py
            ├── test_identifier.py
            ├── test_money.py
            ├── test_date_range.py
            ├── test_event_dispatcher.py
            └── test_specification.py
```

### Цели покрытия:
- 100% для всех базовых классов
- 100% для всех Value Objects
- 100% для Event Dispatcher
- 100% для Specification

---

## ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### День 1: Базовые абстракции
- [ ] Создать структуру папок
- [ ] BaseValueObject + тесты
- [ ] BaseEntity + тесты
- [ ] AggregateRoot + тесты
- [ ] DomainEvent + тесты
- [ ] DomainException + тесты

### День 2: Общие Value Objects
- [ ] Identifier + тесты
- [ ] Money + тесты
- [ ] DateRange + тесты
- [ ] Email + тесты (опционально)
- [ ] PhoneNumber + тесты (опционально)

### День 3: Event Dispatcher & Specification
- [ ] EventDispatcher + тесты
- [ ] EventHandler интерфейс
- [ ] Specification + тесты
- [ ] AndSpecification, OrSpecification, NotSpecification + тесты

### День 4: Документация и рефакторинг
- [ ] Документация для всех классов
- [ ] Примеры использования
- [ ] Рефакторинг
- [ ] Проверка покрытия (100%)

---

**Дата создания:** 2026-03-08  
**Автор:** Kiro AI Assistant  
**Статус:** План готов ✅  
**Следующий этап:** ЭТАП_2_USER_MANAGEMENT_ПЛАН.md

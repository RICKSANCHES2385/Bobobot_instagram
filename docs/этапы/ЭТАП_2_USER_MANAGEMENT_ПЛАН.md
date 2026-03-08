# 🏗️ ЭТАП 2: USER MANAGEMENT CONTEXT - ДЕТАЛЬНЫЙ ПЛАН

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
**Зависимости:** Этап 1 (Shared Kernel) ✅

### Что будет создано:
- User Aggregate с Value Objects
- Use Cases для управления пользователями
- Repository интерфейс и реализация
- Domain Events
- 100% покрытие тестами

---

## ЦЕЛИ И ЗАДАЧИ

### Главная цель:
Создать User Management bounded context - управление пользователями бота с их настройками и языком.

### Задачи:

#### 1. Domain Layer (1 день)
- [ ] Value Objects (UserId, TelegramId, Username, Language)
- [ ] User Aggregate Root
- [ ] Domain Events
- [ ] Repository Interface
- [ ] Domain Exceptions

#### 2. Application Layer (0.5 дня)
- [ ] RegisterUserUseCase
- [ ] GetUserUseCase
- [ ] UpdateUserLanguageUseCase
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

#### UserId
**Файл:** `src/domain/user_management/value_objects/user_id.py`

```python
"""User ID Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.identifier import Identifier


@dataclass(frozen=True)
class UserId(Identifier[int]):
    """User identifier."""
    pass
```

**Тесты:**
- [ ] test_user_id_creation
- [ ] test_user_id_equality
- [ ] test_user_id_hash

---

#### TelegramId
**Файл:** `src/domain/user_management/value_objects/telegram_id.py`

```python
"""Telegram ID Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class TelegramId(BaseValueObject):
    """Telegram user ID."""
    
    value: int
    
    def _validate(self) -> None:
        """Validate Telegram ID."""
        if self.value <= 0:
            raise ValueError("Telegram ID must be positive")
```

**Тесты:**
- [ ] test_telegram_id_creation
- [ ] test_telegram_id_validates_positive
- [ ] test_telegram_id_equality

---

#### Username
**Файл:** `src/domain/user_management/value_objects/username.py`

```python
"""Username Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class Username(BaseValueObject):
    """Telegram username."""
    
    value: str
    
    def _validate(self) -> None:
        """Validate username."""
        if not self.value:
            raise ValueError("Username cannot be empty")
        if len(self.value) > 32:
            raise ValueError("Username too long (max 32 characters)")
        if not self.value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers and underscores")
```

**Тесты:**
- [ ] test_username_creation
- [ ] test_username_validates_empty
- [ ] test_username_validates_length
- [ ] test_username_validates_format

---

#### Language
**Файл:** `src/domain/user_management/value_objects/language.py`

```python
"""Language Value Object."""
from dataclasses import dataclass
from enum import Enum
from src.domain.shared.value_objects.base import BaseValueObject


class LanguageCode(str, Enum):
    """Supported language codes."""
    RU = "ru"
    EN = "en"


@dataclass(frozen=True)
class Language(BaseValueObject):
    """User interface language."""
    
    code: LanguageCode
    
    def _validate(self) -> None:
        """Validate language code."""
        if not isinstance(self.code, LanguageCode):
            raise ValueError(f"Invalid language code: {self.code}")
    
    @classmethod
    def default(cls) -> 'Language':
        """Get default language."""
        return cls(code=LanguageCode.RU)
```

**Тесты:**
- [ ] test_language_creation
- [ ] test_language_default
- [ ] test_language_validates_code

---

### 2. User Aggregate

**Файл:** `src/domain/user_management/aggregates/user.py`

```python
"""User Aggregate Root."""
from dataclasses import dataclass, field
from datetime import datetime
from src.domain.shared.entities.base import AggregateRoot
from ..value_objects.user_id import UserId
from ..value_objects.telegram_id import TelegramId
from ..value_objects.username import Username
from ..value_objects.language import Language
from ..events.user_events import UserRegistered, UserLanguageChanged


@dataclass(eq=False)
class User(AggregateRoot):
    """User aggregate root.
    
    Represents a bot user with their settings and preferences.
    """
    
    telegram_id: TelegramId
    username: Username
    language: Language
    is_active: bool = True
    
    @staticmethod
    def register(
        user_id: UserId,
        telegram_id: TelegramId,
        username: Username,
        language: Language | None = None
    ) -> 'User':
        """Register a new user.
        
        Args:
            user_id: User ID.
            telegram_id: Telegram ID.
            username: Username.
            language: Language (optional, defaults to Russian).
            
        Returns:
            New User instance.
        """
        if language is None:
            language = Language.default()
        
        user = User(
            id=user_id,
            telegram_id=telegram_id,
            username=username,
            language=language
        )
        
        user.add_domain_event(
            UserRegistered(
                user_id=user_id.value,
                telegram_id=telegram_id.value,
                username=username.value
            )
        )
        
        return user
    
    def change_language(self, new_language: Language) -> None:
        """Change user language.
        
        Args:
            new_language: New language.
        """
        if self.language == new_language:
            return
        
        old_language = self.language
        self.language = new_language
        self._touch()
        
        self.add_domain_event(
            UserLanguageChanged(
                user_id=self.id.value,
                old_language=old_language.code.value,
                new_language=new_language.code.value
            )
        )
    
    def deactivate(self) -> None:
        """Deactivate user."""
        self.is_active = False
        self._touch()
    
    def activate(self) -> None:
        """Activate user."""
        self.is_active = True
        self._touch()
```

**Тесты:**
- [ ] test_user_register
- [ ] test_user_register_with_default_language
- [ ] test_user_change_language
- [ ] test_user_change_language_same_language_no_event
- [ ] test_user_deactivate
- [ ] test_user_activate
- [ ] test_user_register_emits_event
- [ ] test_user_change_language_emits_event

---

### 3. Domain Events

**Файл:** `src/domain/user_management/events/user_events.py`

```python
"""User Domain Events."""
from dataclasses import dataclass
from src.domain.shared.events.base import DomainEvent


@dataclass(frozen=True)
class UserRegistered(DomainEvent):
    """User registered event."""
    user_id: int = 0
    telegram_id: int = 0
    username: str = ""


@dataclass(frozen=True)
class UserLanguageChanged(DomainEvent):
    """User language changed event."""
    user_id: int = 0
    old_language: str = ""
    new_language: str = ""
```

**Тесты:**
- [ ] test_user_registered_event_creation
- [ ] test_user_language_changed_event_creation

---

### 4. Repository Interface

**Файл:** `src/domain/user_management/repositories/user_repository.py`

```python
"""User Repository Interface."""
from abc import ABC, abstractmethod
from typing import Optional
from ..aggregates.user import User
from ..value_objects.user_id import UserId
from ..value_objects.telegram_id import TelegramId


class UserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Save user.
        
        Args:
            user: User to save.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID.
            
        Returns:
            User if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: TelegramId) -> Optional[User]:
        """Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram ID.
            
        Returns:
            User if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def exists_by_telegram_id(self, telegram_id: TelegramId) -> bool:
        """Check if user exists by Telegram ID.
        
        Args:
            telegram_id: Telegram ID.
            
        Returns:
            True if exists, False otherwise.
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> None:
        """Delete user.
        
        Args:
            user_id: User ID.
        """
        pass
```

---

### 5. Domain Exceptions

**Файл:** `src/domain/user_management/exceptions.py`

```python
"""User Management Domain Exceptions."""
from src.domain.shared.exceptions.base import DomainException


class UserAlreadyExistsException(DomainException):
    """User already exists."""
    
    def __init__(self, telegram_id: int):
        super().__init__(
            message=f"User with Telegram ID {telegram_id} already exists",
            code="USER_ALREADY_EXISTS"
        )


class UserNotFoundException(DomainException):
    """User not found."""
    
    def __init__(self, identifier: str):
        super().__init__(
            message=f"User not found: {identifier}",
            code="USER_NOT_FOUND"
        )
```

**Тесты:**
- [ ] test_user_already_exists_exception
- [ ] test_user_not_found_exception

---

## APPLICATION LAYER

### 1. DTOs

**Файл:** `src/application/user_management/dtos.py`

```python
"""User Management DTOs."""
from dataclasses import dataclass


@dataclass
class RegisterUserCommand:
    """Register user command."""
    telegram_id: int
    username: str
    language_code: str | None = None


@dataclass
class UpdateUserLanguageCommand:
    """Update user language command."""
    telegram_id: int
    language_code: str


@dataclass
class UserDTO:
    """User data transfer object."""
    id: int
    telegram_id: int
    username: str
    language_code: str
    is_active: bool
    created_at: str
    updated_at: str
```

---

### 2. Use Cases

#### RegisterUserUseCase
**Файл:** `src/application/user_management/use_cases/register_user.py`

```python
"""Register User Use Case."""
from dataclasses import dataclass
from ..dtos import RegisterUserCommand, UserDTO
from ...shared.use_case import UseCase
from ....domain.user_management.aggregates.user import User
from ....domain.user_management.value_objects.user_id import UserId
from ....domain.user_management.value_objects.telegram_id import TelegramId
from ....domain.user_management.value_objects.username import Username
from ....domain.user_management.value_objects.language import Language, LanguageCode
from ....domain.user_management.repositories.user_repository import UserRepository
from ....domain.user_management.exceptions import UserAlreadyExistsException


class RegisterUserUseCase(UseCase[RegisterUserCommand, UserDTO]):
    """Register a new user."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize use case.
        
        Args:
            user_repository: User repository.
        """
        self.user_repository = user_repository
    
    async def execute(self, command: RegisterUserCommand) -> UserDTO:
        """Execute use case.
        
        Args:
            command: Register user command.
            
        Returns:
            User DTO.
            
        Raises:
            UserAlreadyExistsException: If user already exists.
        """
        telegram_id = TelegramId(value=command.telegram_id)
        
        # Check if user already exists
        if await self.user_repository.exists_by_telegram_id(telegram_id):
            raise UserAlreadyExistsException(telegram_id=command.telegram_id)
        
        # Create user
        username = Username(value=command.username)
        language = None
        if command.language_code:
            language = Language(code=LanguageCode(command.language_code))
        
        # Generate new ID (in real app, this would be from DB sequence)
        user_id = UserId(value=0)  # Will be set by repository
        
        user = User.register(
            user_id=user_id,
            telegram_id=telegram_id,
            username=username,
            language=language
        )
        
        # Save user
        await self.user_repository.save(user)
        
        # Return DTO
        return UserDTO(
            id=user.id.value,
            telegram_id=user.telegram_id.value,
            username=user.username.value,
            language_code=user.language.code.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
```

**Тесты:**
- [ ] test_register_user_success
- [ ] test_register_user_with_default_language
- [ ] test_register_user_already_exists_raises
- [ ] test_register_user_invalid_username_raises

---

#### GetUserUseCase
**Файл:** `src/application/user_management/use_cases/get_user.py`

```python
"""Get User Use Case."""
from ..dtos import UserDTO
from ...shared.use_case import UseCase
from ....domain.user_management.value_objects.telegram_id import TelegramId
from ....domain.user_management.repositories.user_repository import UserRepository
from ....domain.user_management.exceptions import UserNotFoundException


class GetUserUseCase(UseCase[int, UserDTO]):
    """Get user by Telegram ID."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize use case.
        
        Args:
            user_repository: User repository.
        """
        self.user_repository = user_repository
    
    async def execute(self, telegram_id: int) -> UserDTO:
        """Execute use case.
        
        Args:
            telegram_id: Telegram ID.
            
        Returns:
            User DTO.
            
        Raises:
            UserNotFoundException: If user not found.
        """
        telegram_id_vo = TelegramId(value=telegram_id)
        user = await self.user_repository.get_by_telegram_id(telegram_id_vo)
        
        if user is None:
            raise UserNotFoundException(identifier=f"telegram_id={telegram_id}")
        
        return UserDTO(
            id=user.id.value,
            telegram_id=user.telegram_id.value,
            username=user.username.value,
            language_code=user.language.code.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
```

**Тесты:**
- [ ] test_get_user_success
- [ ] test_get_user_not_found_raises

---

#### UpdateUserLanguageUseCase
**Файл:** `src/application/user_management/use_cases/update_user_language.py`

```python
"""Update User Language Use Case."""
from ..dtos import UpdateUserLanguageCommand, UserDTO
from ...shared.use_case import UseCase
from ....domain.user_management.value_objects.telegram_id import TelegramId
from ....domain.user_management.value_objects.language import Language, LanguageCode
from ....domain.user_management.repositories.user_repository import UserRepository
from ....domain.user_management.exceptions import UserNotFoundException


class UpdateUserLanguageUseCase(UseCase[UpdateUserLanguageCommand, UserDTO]):
    """Update user language."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize use case.
        
        Args:
            user_repository: User repository.
        """
        self.user_repository = user_repository
    
    async def execute(self, command: UpdateUserLanguageCommand) -> UserDTO:
        """Execute use case.
        
        Args:
            command: Update language command.
            
        Returns:
            User DTO.
            
        Raises:
            UserNotFoundException: If user not found.
        """
        telegram_id = TelegramId(value=command.telegram_id)
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        
        if user is None:
            raise UserNotFoundException(identifier=f"telegram_id={command.telegram_id}")
        
        # Change language
        new_language = Language(code=LanguageCode(command.language_code))
        user.change_language(new_language)
        
        # Save user
        await self.user_repository.save(user)
        
        return UserDTO(
            id=user.id.value,
            telegram_id=user.telegram_id.value,
            username=user.username.value,
            language_code=user.language.code.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
```

**Тесты:**
- [ ] test_update_user_language_success
- [ ] test_update_user_language_user_not_found_raises
- [ ] test_update_user_language_same_language_no_event

---

### 3. Base Use Case

**Файл:** `src/application/shared/use_case.py`

```python
"""Base Use Case."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TCommand = TypeVar('TCommand')
TResult = TypeVar('TResult')


class UseCase(ABC, Generic[TCommand, TResult]):
    """Base use case interface."""
    
    @abstractmethod
    async def execute(self, command: TCommand) -> TResult:
        """Execute use case.
        
        Args:
            command: Command to execute.
            
        Returns:
            Result of execution.
        """
        pass
```

---

## INFRASTRUCTURE LAYER

### 1. SQLAlchemy Models

**Файл:** `src/infrastructure/persistence/models/user_model.py`

```python
"""User SQLAlchemy Model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserModel(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(32), nullable=False)
    language_code = Column(String(2), nullable=False, default="ru")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

### 2. Repository Implementation

**Файл:** `src/infrastructure/persistence/repositories/sqlalchemy_user_repository.py`

```python
"""SQLAlchemy User Repository Implementation."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ....domain.user_management.aggregates.user import User
from ....domain.user_management.value_objects.user_id import UserId
from ....domain.user_management.value_objects.telegram_id import TelegramId
from ....domain.user_management.value_objects.username import Username
from ....domain.user_management.value_objects.language import Language, LanguageCode
from ....domain.user_management.repositories.user_repository import UserRepository
from ..models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of User Repository."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session.
        """
        self.session = session
    
    async def save(self, user: User) -> None:
        """Save user."""
        # Check if user exists
        stmt = select(UserModel).where(UserModel.telegram_id == user.telegram_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            # Create new
            model = UserModel(
                telegram_id=user.telegram_id.value,
                username=user.username.value,
                language_code=user.language.code.value,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            self.session.add(model)
        else:
            # Update existing
            model.username = user.username.value
            model.language_code = user.language.code.value
            model.is_active = user.is_active
            model.updated_at = user.updated_at
        
        await self.session.flush()
        
        # Update user ID
        if user.id.value == 0:
            user.id = UserId(value=model.id)
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._to_domain(model)
    
    async def get_by_telegram_id(self, telegram_id: TelegramId) -> Optional[User]:
        """Get user by Telegram ID."""
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._to_domain(model)
    
    async def exists_by_telegram_id(self, telegram_id: TelegramId) -> bool:
        """Check if user exists."""
        stmt = select(UserModel.id).where(UserModel.telegram_id == telegram_id.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def delete(self, user_id: UserId) -> None:
        """Delete user."""
        stmt = select(UserModel).where(UserModel.id == user_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model is not None:
            await self.session.delete(model)
            await self.session.flush()
    
    def _to_domain(self, model: UserModel) -> User:
        """Convert model to domain entity."""
        user = User(
            id=UserId(value=model.id),
            telegram_id=TelegramId(value=model.telegram_id),
            username=Username(value=model.username),
            language=Language(code=LanguageCode(model.language_code)),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
        return user
```

---

## ТЕСТИРОВАНИЕ

### Структура тестов:
```
tests/
├── unit/
│   ├── domain/
│   │   └── user_management/
│   │       ├── test_user_id.py
│   │       ├── test_telegram_id.py
│   │       ├── test_username.py
│   │       ├── test_language.py
│   │       ├── test_user_aggregate.py
│   │       ├── test_user_events.py
│   │       └── test_user_exceptions.py
│   └── application/
│       └── user_management/
│           ├── test_register_user_use_case.py
│           ├── test_get_user_use_case.py
│           └── test_update_user_language_use_case.py
└── integration/
    └── repositories/
        └── test_sqlalchemy_user_repository.py
```

### Цели покрытия:
- 100% для Domain Layer
- 90%+ для Application Layer
- 80%+ для Infrastructure Layer

---

## ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### День 1: Domain Layer ✅
- [ ] Создать структуру папок
- [ ] UserId + тесты (3 теста)
- [ ] TelegramId + тесты (3 теста)
- [ ] Username + тесты (4 теста)
- [ ] Language + тесты (3 теста)
- [ ] User Aggregate + тесты (8 тестов)
- [ ] Domain Events + тесты (2 теста)
- [ ] Domain Exceptions + тесты (2 теста)
- [ ] Repository Interface

### День 2: Application Layer
- [ ] Base UseCase
- [ ] DTOs
- [ ] RegisterUserUseCase + тесты (4 теста)
- [ ] GetUserUseCase + тесты (2 теста)
- [ ] UpdateUserLanguageUseCase + тесты (3 теста)

### День 3: Infrastructure Layer
- [ ] SQLAlchemy Models
- [ ] SQLAlchemyUserRepository + тесты (6 тестов)
- [ ] Alembic Migration
- [ ] Integration тесты

---

**Дата создания:** 2026-03-08  
**Автор:** Kiro AI Assistant  
**Статус:** План готов ✅  
**Следующий этап:** ЭТАП_3_SUBSCRIPTION_ПЛАН.md

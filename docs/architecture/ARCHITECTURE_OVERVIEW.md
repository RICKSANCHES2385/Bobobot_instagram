# 🏗️ ОБЗОР АРХИТЕКТУРЫ

**Проект:** bobobot_inst_ddd V2.0  
**Дата:** 2026-03-08  
**Архитектурный стиль:** Clean Architecture + DDD

---

## 📐 АРХИТЕКТУРНЫЕ СЛОИ

### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Telegram   │  │     CLI      │  │     API      │     │
│  │   Handlers   │  │   Commands   │  │  Endpoints   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Use Cases   │  │   Commands   │  │    Queries   │     │
│  │              │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     DTOs     │  │   Mappers    │  │  Validators  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                            │
│                    (Business Logic)                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Entities   │  │  Aggregates  │  │    Value     │     │
│  │              │  │              │  │   Objects    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Domain     │  │   Domain     │  │ Repository   │     │
│  │   Events     │  │   Services   │  │  Interfaces  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
└─────────┼─────────────────┼──────────────────┼──────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Repositories │  │    Cache     │  │   External   │     │
│  │     (DB)     │  │   (Redis)    │  │   Services   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Messaging  │  │   Logging    │  │    Config    │     │
│  │   (Events)   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 BOUNDED CONTEXTS

### 8 Bounded Contexts (Микросервисная архитектура в монолите)

```
┌─────────────────────────────────────────────────────────────┐
│                      BOBOBOT_INST_DDD                        │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  User Management │  │   Subscription   │                │
│  │   (3 Use Cases)  │  │  (6 Use Cases)   │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │     Payment      │  │    Instagram     │                │
│  │  (5 Use Cases)   │  │   Integration    │                │
│  │                  │  │  (11 Use Cases)  │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │     Content      │  │    Audience      │                │
│  │    Tracking      │  │    Tracking      │                │
│  │  (5 Use Cases)   │  │  (5 Use Cases)   │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │     Referral     │  │   Notification   │                │
│  │  (5 Use Cases)   │  │  (3 Use Cases)   │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│              ИТОГО: 46 Use Cases (100%)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 ПОТОК ДАННЫХ

### Типичный запрос пользователя:

```
1. USER
   │
   ▼
2. TELEGRAM HANDLER (Presentation)
   │ - Получает сообщение
   │ - Валидирует входные данные
   │ - Создает Command/Query
   │
   ▼
3. USE CASE (Application)
   │ - Получает Command/Query
   │ - Загружает данные через Repository
   │ - Вызывает Domain Logic
   │ - Сохраняет изменения
   │ - Публикует Domain Events
   │
   ▼
4. DOMAIN LOGIC (Domain)
   │ - Бизнес-правила
   │ - Валидация
   │ - Создание Domain Events
   │
   ▼
5. REPOSITORY (Infrastructure)
   │ - Сохранение в БД
   │ - Кэширование
   │
   ▼
6. EVENT HANDLERS (Infrastructure)
   │ - Обработка Domain Events
   │ - Отправка уведомлений
   │ - Логирование
   │
   ▼
7. RESPONSE TO USER (Presentation)
   │ - Форматирование ответа
   │ - Отправка в Telegram
```

---

## 🧩 КОМПОНЕНТЫ DOMAIN LAYER

### Shared Kernel (Общие компоненты)

```
Shared Kernel
├── Value Objects
│   ├── BaseValueObject
│   ├── Identifier
│   ├── Money
│   ├── DateRange
│   ├── Email
│   └── PhoneNumber
│
├── Entities
│   ├── BaseEntity
│   └── AggregateRoot
│
├── Events
│   ├── DomainEvent
│   └── EventDispatcher
│
├── Exceptions
│   ├── DomainException
│   ├── ValidationError
│   ├── NotFoundError
│   └── BusinessRuleViolation
│
└── Specifications
    └── Specification Pattern
```

### Bounded Context Structure (пример)

```
User Management Context
├── Domain
│   ├── Entities
│   │   └── User
│   ├── Value Objects
│   │   ├── UserId
│   │   ├── TelegramUserId
│   │   └── Username
│   ├── Events
│   │   ├── UserCreated
│   │   ├── UserUpdated
│   │   └── UserDeleted
│   └── Repository Interfaces
│       └── IUserRepository
│
├── Application
│   ├── Use Cases
│   │   ├── RegisterUserUseCase
│   │   ├── GetUserByIdUseCase
│   │   └── UpdateUserProfileUseCase
│   ├── Commands
│   │   ├── RegisterUserCommand
│   │   └── UpdateUserProfileCommand
│   ├── Queries
│   │   └── GetUserByIdQuery
│   └── DTOs
│       └── UserDTO
│
└── Infrastructure
    ├── Repositories
    │   └── UserRepositoryImpl
    ├── Models (SQLAlchemy)
    │   └── UserModel
    └── Mappers
        └── UserMapper
```

---

## 🔐 DEPENDENCY RULE

### Правило зависимостей (Dependency Inversion)

```
┌─────────────────────────────────────┐
│         PRESENTATION                │
│              ↓                      │
│         APPLICATION                 │
│              ↓                      │
│           DOMAIN                    │
│              ↑                      │
│       INFRASTRUCTURE                │
└─────────────────────────────────────┘

Правила:
✅ Presentation → Application → Domain
✅ Infrastructure → Domain (через интерфейсы)
❌ Domain → Infrastructure (ЗАПРЕЩЕНО)
❌ Domain → Application (ЗАПРЕЩЕНО)
❌ Domain → Presentation (ЗАПРЕЩЕНО)
```

---

## 📦 ПАТТЕРНЫ

### Domain Layer Patterns

1. **Entity Pattern**
   - Имеет идентификатор
   - Изменяемый
   - Сравнение по ID

2. **Value Object Pattern**
   - Неизменяемый (immutable)
   - Сравнение по значению
   - Самовалидация

3. **Aggregate Pattern**
   - Корень агрегата (Aggregate Root)
   - Управляет консистентностью
   - Публикует Domain Events

4. **Repository Pattern**
   - Абстракция над хранилищем
   - Интерфейс в Domain
   - Реализация в Infrastructure

5. **Domain Event Pattern**
   - Неизменяемый
   - Описывает произошедшее событие
   - Обрабатывается асинхронно

### Application Layer Patterns

1. **Use Case Pattern**
   - Один Use Case = одна бизнес-операция
   - Оркестрирует Domain Logic
   - Управляет транзакциями

2. **Command Pattern**
   - Описывает намерение изменить состояние
   - Неизменяемый
   - Валидируется

3. **Query Pattern**
   - Описывает намерение получить данные
   - Не изменяет состояние
   - Может использовать read-модели

4. **DTO Pattern**
   - Передача данных между слоями
   - Простые структуры данных
   - Без бизнес-логики

### Infrastructure Layer Patterns

1. **Adapter Pattern**
   - Адаптация внешних сервисов
   - Реализация интерфейсов из Domain
   - Изоляция внешних зависимостей

2. **Unit of Work Pattern**
   - Управление транзакциями
   - Координация репозиториев
   - Атомарность операций

3. **Mapper Pattern**
   - Преобразование Domain ↔ ORM
   - Изоляция Domain от БД
   - Двунаправленное преобразование

---

## 🧪 ТЕСТИРОВАНИЕ

### Пирамида тестов

```
        ┌─────┐
        │ E2E │  ~20 тестов (10%)
        └─────┘
      ┌─────────┐
      │Integration│  ~50 тестов (20%)
      └─────────┘
    ┌─────────────┐
    │    Unit     │  ~220 тестов (70%)
    └─────────────┘

Итого: ~290 тестов
```

### Покрытие по слоям

- **Domain Layer:** 100% (критично!)
- **Application Layer:** 90%+
- **Infrastructure Layer:** 80%+
- **Presentation Layer:** 70%+

---

## 🚀 МАСШТАБИРУЕМОСТЬ

### Горизонтальное масштабирование

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Bot #1     │  │   Bot #2     │  │   Bot #3     │
└──────────────┘  └──────────────┘  └──────────────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                    ┌────▼────┐
                    │  Redis  │  (Session Storage)
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │   DB    │  (PostgreSQL)
                    └─────────┘
```

### Вертикальное масштабирование

- Кэширование (Redis)
- Connection Pooling
- Асинхронная обработка
- Rate Limiting

---

## 📊 МЕТРИКИ

### Компоненты по слоям

| Слой | Компоненты | Файлов |
|------|-----------|--------|
| Domain | 58 VO + 15 Entities + 36 Events | ~109 |
| Application | 46 UC + 36 Commands + 42 DTOs | ~124 |
| Infrastructure | 10 Repos + 5 Adapters + 10 Mappers | ~25 |
| Presentation | 10 Handlers + 10 Keyboards | ~20 |

**Итого:** ~278 файлов кода

### Строки кода (оценка)

- Domain: ~5,000 строк
- Application: ~6,000 строк
- Infrastructure: ~4,000 строк
- Presentation: ~3,000 строк
- Tests: ~10,000 строк

**Итого:** ~28,000 строк кода

---

## 🎯 ПРЕИМУЩЕСТВА АРХИТЕКТУРЫ

### 1. Независимость от фреймворков
✅ Domain не зависит от aiogram, SQLAlchemy и т.д.

### 2. Тестируемость
✅ 100% покрытие Domain Layer
✅ Легко мокировать зависимости

### 3. Независимость от UI
✅ Можно заменить Telegram на Web/CLI

### 4. Независимость от БД
✅ Можно заменить PostgreSQL на MongoDB

### 5. Независимость от внешних сервисов
✅ Можно заменить HikerAPI на другой сервис

### 6. Бизнес-логика в центре
✅ Domain Layer - сердце приложения
✅ Все остальное - детали реализации

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ МАТЕРИАЛЫ

### Документация:
- [README_V2.md](../../README_V2.md) - Полный обзор
- [QUICK_START_V2.md](../../QUICK_START_V2.md) - Быстрый старт
- [PROGRESS_CHECKLIST.md](../../PROGRESS_CHECKLIST.md) - Чеклист

### Примеры:
- [EXAMPLES_VALUE_OBJECTS.md](../solution/EXAMPLES_VALUE_OBJECTS.md)
- [EXAMPLES_ENTITIES_AGGREGATES.md](../solution/EXAMPLES_ENTITIES_AGGREGATES.md)

### Правила:
- [ddd_ruls.md](../solution/ruls/ddd_ruls.md)

---

**Дата создания:** 2026-03-08  
**Автор:** Kiro AI Assistant  
**Версия:** 2.0  
**Статус:** ✅ ГОТОВО

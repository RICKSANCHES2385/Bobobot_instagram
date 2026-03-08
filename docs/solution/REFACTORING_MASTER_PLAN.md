# 🏗️ МАСТЕР-ПЛАН РЕФАКТОРИНГА INSTAGRAM BOT НА DDD АРХИТЕКТУРУ

## 📋 ОГЛАВЛЕНИЕ
1. [Анализ текущей архитектуры](#1-анализ-текущей-архитектуры)
2. [Целевая DDD архитектура](#2-целевая-ddd-архитектура)
3. [Bounded Contexts (Ограниченные контексты)](#3-bounded-contexts)
4. [Детальная структура проекта](#4-детальная-структура-проекта)
5. [Пошаговый план миграции](#5-пошаговый-план-миграции)
6. [Паттерны проектирования](#6-паттерны-проектирования)
7. [Тестирование](#7-тестирование)
8. [Метрики успеха](#8-метрики-успеха)

---

## 1. АНАЛИЗ ТЕКУЩЕЙ АРХИТЕКТУРЫ

### 1.1 Текущая структура (Анемичная модель)
```
bobobot_inst/src/
├── bot.py                          # Точка входа + бизнес-логика
├── config.py                       # Конфигурация
├── keyboards.py                    # UI логика
├── handlers/                       # Обработчики команд (толстые контроллеры)
│   ├── commands.py                 # 1127 строк! Нарушение SRP
│   ├── instagram_handlers.py      # Смешана бизнес-логика с UI
│   ├── payment_handlers.py
│   ├── tracking_menu.py
│   └── stories_handler.py
├── services/                       # Сервисы (но не доменные!)
│   ├── hikerapi_client.py         # Инфраструктура в сервисах
│   ├── subscription_manager.py    # Анемичный сервис
│   ├── tracking_service.py
│   ├── audience_tracking_manager.py
│   └── user_repository.py         # Репозиторий, но без UoW
├── models/                         # Анемичные модели (только данные)
│   ├── user.py
│   ├── subscription.py
│   ├── payment.py
│   ├── instagram_tracking.py
│   └── audience_tracking_subscription.py
└── utils/
    └── logger.py
```

### 1.2 Проблемы текущей архитектуры


#### ❌ Нарушения принципов:
1. **Анемичная доменная модель** - модели без поведения, вся логика в сервисах
2. **Нарушение SRP** - handlers содержат UI + бизнес-логику + оркестрацию
3. **Отсутствие Bounded Contexts** - все в одной куче
4. **Нет Unit of Work** - транзакции разбросаны по коду
5. **Инфраструктура смешана с доменом** - HikerAPI в services/
6. **Толстые контроллеры** - commands.py 1127 строк
7. **Дублирование логики** - валидация, форматирование разбросаны
8. **Слабая типизация** - отсутствие Value Objects
9. **Нет доменных событий** - сложно отследить бизнес-процессы
10. **Тестирование затруднено** - зависимости не инвертированы

#### 🔍 Выявленные Bounded Contexts:
1. **User Management** - пользователи, регистрация, профили
2. **Subscription** - подписки, тарифы, пробные периоды
3. **Payment** - платежи (Stars, Robokassa, CryptoBot)
4. **Instagram Integration** - работа с Instagram API
5. **Content Tracking** - отслеживание контента (stories, posts)
6. **Audience Tracking** - отслеживание аудитории (followers/following)
7. **Referral** - реферальная система
8. **Notification** - уведомления пользователей

---

## 2. ЦЕЛЕВАЯ DDD АРХИТЕКТУРА

### 2.1 Принципы новой архитектуры

#### ✅ Ключевые принципы:
1. **Rich Domain Model** - модели с поведением
2. **Bounded Contexts** - четкое разделение доменов
3. **Ubiquitous Language** - единый язык в коде и документации
4. **Layered Architecture** - строгое разделение слоев
5. **Dependency Inversion** - зависимости направлены к домену
6. **CQRS** - разделение команд и запросов
7. **Domain Events** - асинхронная коммуникация между контекстами
8. **Unit of Work** - управление транзакциями
9. **Repository Pattern** - абстракция доступа к данным
10. **Value Objects** - неизменяемые объекты значений

### 2.2 Слои архитектуры (Hexagonal/Clean)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  (Telegram Handlers, CLI, API - Adapters)                   │
│  - Тонкие контроллеры                                        │
│  - Маршрутизация запросов                                    │
│  - Сериализация/десериализация                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  (Use Cases, Application Services, DTOs)                    │
│  - Оркестрация бизнес-логики                                 │
│  - Координация между доменами                                │
│  - Управление транзакциями (UoW)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                             │
│  (Entities, Value Objects, Domain Services, Events)         │
│  - Бизнес-логика                                             │
│  - Инварианты домена                                         │
│  - Доменные события                                          │
│  - Агрегаты                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                        │
│  (Repositories, External APIs, Database, Cache)             │
│  - Реализация репозиториев                                   │
│  - Внешние сервисы (HikerAPI, CryptoBot)                    │
│  - База данных, Redis                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. BOUNDED CONTEXTS (Ограниченные контексты)

### 3.1 User Management Context
**Ответственность:** Управление пользователями, аутентификация, профили

#### Entities:
- `User` (Aggregate Root)
  - UserId (Value Object)
  - TelegramId (Value Object)
  - Username (Value Object)
  - Profile (Value Object)
  - Language (Value Object)

#### Value Objects:
- `UserId` - уникальный идентификатор
- `TelegramId` - Telegram ID
- `Username` - имя пользователя
- `Profile` - профиль (first_name, last_name)
- `Language` - язык интерфейса

#### Domain Events:
- `UserRegistered` - пользователь зарегистрирован
- `UserProfileUpdated` - профиль обновлен
- `UserLanguageChanged` - язык изменен

#### Use Cases:
- `RegisterUserUseCase` - регистрация пользователя
- `UpdateUserProfileUseCase` - обновление профиля
- `GetUserByTelegramIdUseCase` - получение пользователя

#### Repository Interfaces:
- `IUserRepository` - интерфейс репозитория пользователей

---

### 3.2 Subscription Context
**Ответственность:** Управление подписками, тарифами, пробными периодами


#### Entities:
- `Subscription` (Aggregate Root)
  - SubscriptionId (Value Object)
  - UserId (Value Object)
  - SubscriptionType (Enum: FREE, PAID)
  - Period (Value Object)
  - Status (Value Object)
  - Methods: activate(), extend(), cancel(), isExpired()

- `SubscriptionPlan`
  - PlanId (Value Object)
  - Name (Value Object)
  - Duration (Value Object)
  - Pricing (Value Object - multi-currency)

#### Value Objects:
- `SubscriptionId` - ID подписки
- `SubscriptionType` - тип (FREE/PAID)
- `Period` - период (start_date, end_date)
- `Duration` - длительность (days)
- `Pricing` - цены (stars, rub, ton, usdt)
- `SubscriptionStatus` - статус (ACTIVE, EXPIRED, CANCELLED)

#### Domain Events:
- `SubscriptionActivated` - подписка активирована
- `SubscriptionExtended` - подписка продлена
- `SubscriptionExpired` - подписка истекла
- `SubscriptionCancelled` - подписка отменена
- `TrialSubscriptionCreated` - создана пробная подписка

#### Domain Services:
- `SubscriptionExpirationService` - проверка истечения
- `SubscriptionPricingService` - расчет цен

#### Use Cases:
- `ActivateSubscriptionUseCase` - активация подписки
- `ExtendSubscriptionUseCase` - продление подписки
- `CancelSubscriptionUseCase` - отмена подписки
- `CheckSubscriptionStatusUseCase` - проверка статуса
- `CreateTrialSubscriptionUseCase` - создание пробной подписки
- `GetAvailablePlansUseCase` - получение доступных тарифов

#### Repository Interfaces:
- `ISubscriptionRepository` - репозиторий подписок
- `ISubscriptionPlanRepository` - репозиторий тарифов

---

### 3.3 Payment Context
**Ответственность:** Обработка платежей через разные провайдеры

#### Entities:
- `Payment` (Aggregate Root)
  - PaymentId (Value Object)
  - UserId (Value Object)
  - Amount (Value Object)
  - Currency (Value Object)
  - PaymentMethod (Value Object)
  - Status (Value Object)
  - Methods: process(), complete(), fail(), refund()

- `Invoice`
  - InvoiceId (Value Object)
  - PaymentId (Value Object)
  - Amount (Value Object)
  - Description (Value Object)

#### Value Objects:
- `PaymentId` - ID платежа
- `InvoiceId` - ID счета
- `Amount` - сумма
- `Currency` - валюта (XTR, RUB, TON, USDT)
- `PaymentMethod` - метод (TELEGRAM_STARS, ROBOKASSA, CRYPTO_BOT)
- `PaymentStatus` - статус (PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED)
- `ProviderPaymentId` - ID платежа у провайдера

#### Domain Events:
- `PaymentCreated` - платеж создан
- `PaymentProcessing` - платеж обрабатывается
- `PaymentCompleted` - платеж завершен
- `PaymentFailed` - платеж провален
- `PaymentRefunded` - платеж возвращен

#### Domain Services:
- `PaymentProcessingService` - обработка платежей
- `InvoiceGenerationService` - генерация счетов

#### Use Cases:
- `CreatePaymentUseCase` - создание платежа
- `ProcessPaymentUseCase` - обработка платежа
- `CompletePaymentUseCase` - завершение платежа
- `RefundPaymentUseCase` - возврат платежа
- `GetPaymentStatusUseCase` - получение статуса

#### Repository Interfaces:
- `IPaymentRepository` - репозиторий платежей

#### External Service Interfaces (Ports):
- `ITelegramStarsPaymentGateway` - Telegram Stars
- `IRobokassaPaymentGateway` - Robokassa
- `ICryptoBotPaymentGateway` - CryptoBot

---

### 3.4 Instagram Integration Context
**Ответственность:** Интеграция с Instagram API, получение данных профилей

#### Entities:
- `InstagramProfile` (Aggregate Root)
  - ProfileId (Value Object)
  - Username (Value Object)
  - UserId (Value Object)
  - Statistics (Value Object)
  - Bio (Value Object)
  - Methods: updateStatistics(), isPrivate()

- `InstagramRequest`
  - RequestId (Value Object)
  - UserId (Value Object)
  - ProfileId (Value Object)
  - RequestType (Value Object)
  - Timestamp (Value Object)

#### Value Objects:
- `InstagramUsername` - username Instagram
- `InstagramUserId` - ID пользователя Instagram
- `ProfileStatistics` - статистика (followers, following, posts)
- `Bio` - биография
- `ProfilePicture` - URL аватара
- `RequestType` - тип запроса (PROFILE, STORIES, POSTS, etc.)

#### Domain Events:
- `ProfileDataFetched` - данные профиля получены
- `ProfileNotFound` - профиль не найден
- `ProfileIsPrivate` - профиль приватный
- `RateLimitExceeded` - превышен лимит запросов

#### Domain Services:
- `RateLimitingService` - контроль лимитов
- `CacheService` - кэширование данных

#### Use Cases:
- `FetchInstagramProfileUseCase` - получение профиля
- `FetchInstagramStoriesUseCase` - получение stories
- `FetchInstagramPostsUseCase` - получение постов
- `FetchInstagramReelsUseCase` - получение reels
- `SearchInstagramUsersUseCase` - поиск пользователей

#### Repository Interfaces:
- `IInstagramRequestRepository` - репозиторий запросов

#### External Service Interfaces (Ports):
- `IInstagramAPIClient` - клиент Instagram API (HikerAPI)

---

### 3.5 Content Tracking Context
**Ответственность:** Отслеживание контента (stories, posts, reels)


#### Entities:
- `ContentTracking` (Aggregate Root)
  - TrackingId (Value Object)
  - UserId (Value Object)
  - TargetProfile (Value Object)
  - TrackingSettings (Value Object)
  - Status (Value Object)
  - Methods: activate(), deactivate(), updateSettings(), shouldCheck()

- `TrackedContent`
  - ContentId (Value Object)
  - TrackingId (Value Object)
  - ContentType (Value Object)
  - ContentData (Value Object)
  - DetectedAt (Value Object)

#### Value Objects:
- `TrackingId` - ID отслеживания
- `TargetProfile` - целевой профиль (username, user_id)
- `TrackingSettings` - настройки (types, intervals)
- `ContentType` - тип контента (STORY, POST, REEL)
- `CheckInterval` - интервал проверки (1h, 6h, 12h, 24h)
- `TrackingStatus` - статус (ACTIVE, PAUSED, CANCELLED)

#### Domain Events:
- `TrackingActivated` - отслеживание активировано
- `TrackingDeactivated` - отслеживание деактивировано
- `NewContentDetected` - обнаружен новый контент
- `TrackingCheckCompleted` - проверка завершена
- `TrackingCheckFailed` - проверка провалена

#### Domain Services:
- `ContentDetectionService` - обнаружение нового контента
- `TrackingSchedulerService` - планирование проверок

#### Use Cases:
- `ActivateContentTrackingUseCase` - активация отслеживания
- `DeactivateContentTrackingUseCase` - деактивация
- `UpdateTrackingSettingsUseCase` - обновление настроек
- `CheckTrackingUpdatesUseCase` - проверка обновлений
- `GetUserTrackingsUseCase` - получение отслеживаний пользователя

#### Repository Interfaces:
- `IContentTrackingRepository` - репозиторий отслеживаний
- `ITrackedContentRepository` - репозиторий отслеженного контента

---

### 3.6 Audience Tracking Context
**Ответственность:** Платное отслеживание аудитории (followers/following)

#### Entities:
- `AudienceTracking` (Aggregate Root)
  - TrackingId (Value Object)
  - UserId (Value Object)
  - TargetProfile (Value Object)
  - Subscription (Value Object)
  - AudienceSnapshot (Value Object)
  - Methods: activate(), deactivate(), updateSnapshot(), detectChanges()

- `AudienceChange`
  - ChangeId (Value Object)
  - TrackingId (Value Object)
  - ChangeType (Value Object)
  - AffectedUsers (Value Object)
  - DetectedAt (Value Object)

#### Value Objects:
- `AudienceTrackingId` - ID отслеживания аудитории
- `AudienceSubscription` - подписка (expires_at, is_active)
- `AudienceSnapshot` - снимок аудитории (followers_count, following_count)
- `FollowerLimit` - лимит подписчиков (100,000)
- `AudienceChangeType` - тип изменения (NEW_FOLLOWER, UNFOLLOWED, etc.)
- `AudiencePricing` - цена (576 followers + 129 RUB/month)

#### Domain Events:
- `AudienceTrackingActivated` - отслеживание активировано
- `AudienceTrackingExpired` - подписка истекла
- `NewFollowerDetected` - новый подписчик
- `UnfollowDetected` - отписка
- `FollowerLimitExceeded` - превышен лимит подписчиков

#### Domain Services:
- `AudienceComparisonService` - сравнение аудитории
- `AudiencePricingService` - расчет цен

#### Use Cases:
- `ActivateAudienceTrackingUseCase` - активация отслеживания
- `DeactivateAudienceTrackingUseCase` - деактивация
- `CheckAudienceChangesUseCase` - проверка изменений
- `GetAudienceTrackingStatusUseCase` - получение статуса
- `CalculateAudienceTrackingPriceUseCase` - расчет цены

#### Repository Interfaces:
- `IAudienceTrackingRepository` - репозиторий отслеживаний
- `IAudienceChangeRepository` - репозиторий изменений

---

### 3.7 Referral Context
**Ответственность:** Реферальная система, бонусы, комиссии

#### Entities:
- `Referral` (Aggregate Root)
  - ReferralId (Value Object)
  - ReferrerId (Value Object)
  - ReferredId (Value Object)
  - ReferralCode (Value Object)
  - Rewards (Value Object)
  - Status (Value Object)
  - Methods: activate(), grantReward(), calculateCommission()

- `ReferralStats`
  - StatsId (Value Object)
  - UserId (Value Object)
  - TotalReferrals (Value Object)
  - TotalRewards (Value Object)

#### Value Objects:
- `ReferralId` - ID реферала
- `ReferralCode` - реферальный код
- `CommissionRate` - ставка комиссии (5%)
- `Rewards` - награды (usdt, ton, stars, rub)
- `ReferralStatus` - статус (ACTIVE, INACTIVE, REWARDED)

#### Domain Events:
- `ReferralCreated` - реферал создан
- `ReferralActivated` - реферал активирован
- `ReferralRewardGranted` - награда выдана
- `ReferralPaymentReceived` - получен платеж от реферала

#### Domain Services:
- `ReferralCommissionService` - расчет комиссий
- `ReferralLinkGenerationService` - генерация ссылок

#### Use Cases:
- `CreateReferralUseCase` - создание реферала
- `ApplyReferralCodeUseCase` - применение кода
- `GrantReferralRewardUseCase` - выдача награды
- `GetReferralStatsUseCase` - получение статистики
- `GenerateReferralLinkUseCase` - генерация ссылки

#### Repository Interfaces:
- `IReferralRepository` - репозиторий рефералов
- `IReferralStatsRepository` - репозиторий статистики

---

### 3.8 Notification Context
**Ответственность:** Отправка уведомлений пользователям


#### Entities:
- `Notification` (Aggregate Root)
  - NotificationId (Value Object)
  - RecipientId (Value Object)
  - NotificationType (Value Object)
  - Content (Value Object)
  - Status (Value Object)
  - Methods: send(), markAsRead(), retry()

#### Value Objects:
- `NotificationId` - ID уведомления
- `NotificationType` - тип (NEW_CONTENT, SUBSCRIPTION_EXPIRING, PAYMENT_SUCCESS, etc.)
- `NotificationContent` - содержимое (text, media, keyboard)
- `NotificationStatus` - статус (PENDING, SENT, FAILED, READ)

#### Domain Events:
- `NotificationCreated` - уведомление создано
- `NotificationSent` - уведомление отправлено
- `NotificationFailed` - отправка провалена
- `NotificationRead` - уведомление прочитано

#### Use Cases:
- `SendNotificationUseCase` - отправка уведомления
- `SendBulkNotificationsUseCase` - массовая отправка
- `RetryFailedNotificationsUseCase` - повтор неудачных

#### Repository Interfaces:
- `INotificationRepository` - репозиторий уведомлений

#### External Service Interfaces (Ports):
- `ITelegramNotificationService` - сервис отправки в Telegram

---

## 4. ДЕТАЛЬНАЯ СТРУКТУРА ПРОЕКТА

### 4.1 Полная структура директорий


```
bobobot_inst_ddd/
├── src/
│   ├── domain/                                 # DOMAIN LAYER
│   │   ├── __init__.py
│   │   ├── shared/                             # Shared Kernel
│   │   │   ├── __init__.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                     # BaseValueObject
│   │   │   │   ├── identifier.py               # ID base class
│   │   │   │   ├── money.py                    # Money VO
│   │   │   │   └── date_range.py               # DateRange VO
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── base.py                     # BaseEntity, AggregateRoot
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                     # DomainEvent base
│   │   │   │   └── event_dispatcher.py         # Event dispatcher
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                     # DomainException
│   │   │   │   └── validation.py               # ValidationException
│   │   │   └── specifications/
│   │   │       ├── __init__.py
│   │   │       └── base.py                     # Specification pattern
│   │   │
│   │   ├── user_management/                    # User Management BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user.py                     # User aggregate
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_id.py
│   │   │   │   ├── telegram_id.py
│   │   │   │   ├── username.py
│   │   │   │   ├── profile.py
│   │   │   │   └── language.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_registered.py
│   │   │   │   ├── user_profile_updated.py
│   │   │   │   └── user_language_changed.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_not_found.py
│   │   │   │   └── invalid_telegram_id.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── user_repository.py          # IUserRepository interface
│   │   │
│   │   ├── subscription/                       # Subscription BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── subscription.py             # Subscription aggregate
│   │   │   │   └── subscription_plan.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── subscription_id.py
│   │   │   │   ├── subscription_type.py
│   │   │   │   ├── period.py
│   │   │   │   ├── duration.py
│   │   │   │   ├── pricing.py
│   │   │   │   └── subscription_status.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── subscription_activated.py
│   │   │   │   ├── subscription_extended.py
│   │   │   │   ├── subscription_expired.py
│   │   │   │   ├── subscription_cancelled.py
│   │   │   │   └── trial_subscription_created.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── subscription_expiration_service.py
│   │   │   │   └── subscription_pricing_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── subscription_not_found.py
│   │   │   │   ├── subscription_already_active.py
│   │   │   │   └── subscription_expired.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── subscription_repository.py
│   │   │       └── subscription_plan_repository.py
│   │   │
│   │   ├── payment/                            # Payment BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── payment.py                  # Payment aggregate
│   │   │   │   └── invoice.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── payment_id.py
│   │   │   │   ├── invoice_id.py
│   │   │   │   ├── amount.py
│   │   │   │   ├── currency.py
│   │   │   │   ├── payment_method.py
│   │   │   │   ├── payment_status.py
│   │   │   │   └── provider_payment_id.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── payment_created.py
│   │   │   │   ├── payment_processing.py
│   │   │   │   ├── payment_completed.py
│   │   │   │   ├── payment_failed.py
│   │   │   │   └── payment_refunded.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── payment_processing_service.py
│   │   │   │   └── invoice_generation_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── payment_not_found.py
│   │   │   │   ├── invalid_amount.py
│   │   │   │   └── payment_already_processed.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── payment_repository.py
│   │   │
│   │   ├── instagram_integration/              # Instagram Integration BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instagram_profile.py
│   │   │   │   └── instagram_request.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instagram_username.py
│   │   │   │   ├── instagram_user_id.py
│   │   │   │   ├── profile_statistics.py
│   │   │   │   ├── bio.py
│   │   │   │   └── request_type.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── profile_data_fetched.py
│   │   │   │   ├── profile_not_found.py
│   │   │   │   ├── profile_is_private.py
│   │   │   │   └── rate_limit_exceeded.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rate_limiting_service.py
│   │   │   │   └── cache_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── profile_not_found.py
│   │   │   │   ├── private_profile.py
│   │   │   │   └── rate_limit_exceeded.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── instagram_request_repository.py
│   │   │
│   │   ├── content_tracking/                   # Content Tracking BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── content_tracking.py
│   │   │   │   └── tracked_content.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tracking_id.py
│   │   │   │   ├── target_profile.py
│   │   │   │   ├── tracking_settings.py
│   │   │   │   ├── content_type.py
│   │   │   │   ├── check_interval.py
│   │   │   │   └── tracking_status.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tracking_activated.py
│   │   │   │   ├── tracking_deactivated.py
│   │   │   │   ├── new_content_detected.py
│   │   │   │   ├── tracking_check_completed.py
│   │   │   │   └── tracking_check_failed.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── content_detection_service.py
│   │   │   │   └── tracking_scheduler_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tracking_not_found.py
│   │   │   │   └── tracking_already_exists.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── content_tracking_repository.py
│   │   │       └── tracked_content_repository.py
│   │   │
│   │   ├── audience_tracking/                  # Audience Tracking BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audience_tracking.py
│   │   │   │   └── audience_change.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audience_tracking_id.py
│   │   │   │   ├── audience_subscription.py
│   │   │   │   ├── audience_snapshot.py
│   │   │   │   ├── follower_limit.py
│   │   │   │   ├── audience_change_type.py
│   │   │   │   └── audience_pricing.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audience_tracking_activated.py
│   │   │   │   ├── audience_tracking_expired.py
│   │   │   │   ├── new_follower_detected.py
│   │   │   │   ├── unfollow_detected.py
│   │   │   │   └── follower_limit_exceeded.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audience_comparison_service.py
│   │   │   │   └── audience_pricing_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── follower_limit_exceeded.py
│   │   │   │   └── audience_tracking_expired.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── audience_tracking_repository.py
│   │   │       └── audience_change_repository.py
│   │   │
│   │   ├── referral/                           # Referral BC
│   │   │   ├── __init__.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── referral.py
│   │   │   │   └── referral_stats.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── referral_id.py
│   │   │   │   ├── referral_code.py
│   │   │   │   ├── commission_rate.py
│   │   │   │   ├── rewards.py
│   │   │   │   └── referral_status.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── referral_created.py
│   │   │   │   ├── referral_activated.py
│   │   │   │   ├── referral_reward_granted.py
│   │   │   │   └── referral_payment_received.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── referral_commission_service.py
│   │   │   │   └── referral_link_generation_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── referral_not_found.py
│   │   │   │   └── invalid_referral_code.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       ├── referral_repository.py
│   │   │       └── referral_stats_repository.py
│   │   │
│   │   └── notification/                       # Notification BC
│   │       ├── __init__.py
│   │       ├── entities/
│   │       │   ├── __init__.py
│   │       │   └── notification.py
│   │       ├── value_objects/
│   │       │   ├── __init__.py
│   │       │   ├── notification_id.py
│   │       │   ├── notification_type.py
│   │       │   ├── notification_content.py
│   │       │   └── notification_status.py
│   │       ├── events/
│   │       │   ├── __init__.py
│   │       │   ├── notification_created.py
│   │       │   ├── notification_sent.py
│   │       │   ├── notification_failed.py
│   │       │   └── notification_read.py
│   │       ├── exceptions/
│   │       │   ├── __init__.py
│   │       │   └── notification_send_failed.py
│   │       └── repositories/
│   │           ├── __init__.py
│   │           └── notification_repository.py
│   │
│   ├── application/                            # APPLICATION LAYER
│   │   ├── __init__.py
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── unit_of_work.py                 # IUnitOfWork interface
│   │   │   ├── command.py                      # Command base
│   │   │   ├── query.py                        # Query base
│   │   │   ├── dto.py                          # DTO base
│   │   │   └── result.py                       # Result pattern
│   │   │
│   │   ├── user_management/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── register_user.py
│   │   │   │   └── update_user_profile.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_user_by_telegram_id.py
│   │   │   │   └── get_user_by_id.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_dto.py
│   │   │   │   └── user_profile_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── register_user_use_case.py
│   │   │       ├── update_user_profile_use_case.py
│   │   │       └── get_user_by_telegram_id_use_case.py
│   │   │
│   │   ├── subscription/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── activate_subscription.py
│   │   │   │   ├── extend_subscription.py
│   │   │   │   ├── cancel_subscription.py
│   │   │   │   └── create_trial_subscription.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_active_subscription.py
│   │   │   │   ├── get_subscription_status.py
│   │   │   │   └── get_available_plans.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── subscription_dto.py
│   │   │   │   └── subscription_plan_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── activate_subscription_use_case.py
│   │   │       ├── extend_subscription_use_case.py
│   │   │       ├── cancel_subscription_use_case.py
│   │   │       ├── check_subscription_status_use_case.py
│   │   │       ├── create_trial_subscription_use_case.py
│   │   │       └── get_available_plans_use_case.py
│   │   │
│   │   ├── payment/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_payment.py
│   │   │   │   ├── process_payment.py
│   │   │   │   ├── complete_payment.py
│   │   │   │   └── refund_payment.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_payment_status.py
│   │   │   │   └── get_user_payments.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── payment_dto.py
│   │   │   │   └── invoice_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── create_payment_use_case.py
│   │   │       ├── process_payment_use_case.py
│   │   │       ├── complete_payment_use_case.py
│   │   │       ├── refund_payment_use_case.py
│   │   │       └── get_payment_status_use_case.py
│   │   │
│   │   ├── instagram_integration/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   └── fetch_instagram_profile.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_instagram_profile.py
│   │   │   │   ├── get_instagram_stories.py
│   │   │   │   ├── get_instagram_posts.py
│   │   │   │   └── search_instagram_users.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instagram_profile_dto.py
│   │   │   │   └── instagram_content_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── fetch_instagram_profile_use_case.py
│   │   │       ├── fetch_instagram_stories_use_case.py
│   │   │       ├── fetch_instagram_posts_use_case.py
│   │   │       ├── fetch_instagram_reels_use_case.py
│   │   │       └── search_instagram_users_use_case.py
│   │   │
│   │   ├── content_tracking/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── activate_content_tracking.py
│   │   │   │   ├── deactivate_content_tracking.py
│   │   │   │   └── update_tracking_settings.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_user_trackings.py
│   │   │   │   └── get_tracking_status.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── content_tracking_dto.py
│   │   │   │   └── tracked_content_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── activate_content_tracking_use_case.py
│   │   │       ├── deactivate_content_tracking_use_case.py
│   │   │       ├── update_tracking_settings_use_case.py
│   │   │       ├── check_tracking_updates_use_case.py
│   │   │       └── get_user_trackings_use_case.py
│   │   │
│   │   ├── audience_tracking/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── activate_audience_tracking.py
│   │   │   │   └── deactivate_audience_tracking.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_audience_tracking_status.py
│   │   │   │   └── calculate_audience_tracking_price.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── audience_tracking_dto.py
│   │   │   │   └── audience_change_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── activate_audience_tracking_use_case.py
│   │   │       ├── deactivate_audience_tracking_use_case.py
│   │   │       ├── check_audience_changes_use_case.py
│   │   │       ├── get_audience_tracking_status_use_case.py
│   │   │       └── calculate_audience_tracking_price_use_case.py
│   │   │
│   │   ├── referral/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_referral.py
│   │   │   │   ├── apply_referral_code.py
│   │   │   │   └── grant_referral_reward.py
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_referral_stats.py
│   │   │   │   └── generate_referral_link.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── referral_dto.py
│   │   │   │   └── referral_stats_dto.py
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── create_referral_use_case.py
│   │   │       ├── apply_referral_code_use_case.py
│   │   │       ├── grant_referral_reward_use_case.py
│   │   │       ├── get_referral_stats_use_case.py
│   │   │       └── generate_referral_link_use_case.py
│   │   │
│   │   └── notification/
│   │       ├── __init__.py
│   │       ├── commands/
│   │       │   ├── __init__.py
│   │       │   ├── send_notification.py
│   │       │   └── send_bulk_notifications.py
│   │       ├── queries/
│   │       │   ├── __init__.py
│   │       │   └── get_notification_status.py
│   │       ├── dtos/
│   │       │   ├── __init__.py
│   │       │   └── notification_dto.py
│   │       └── use_cases/
│   │           ├── __init__.py
│   │           ├── send_notification_use_case.py
│   │           ├── send_bulk_notifications_use_case.py
│   │           └── retry_failed_notifications_use_case.py
│   │
│   ├── infrastructure/                         # INFRASTRUCTURE LAYER
│   │   ├── __init__.py
│   │   ├── persistence/
│   │   │   ├── __init__.py
│   │   │   ├── database.py                     # Database connection
│   │   │   ├── unit_of_work.py                 # UnitOfWork implementation
│   │   │   ├── sqlalchemy/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models/                     # SQLAlchemy models
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user_model.py
│   │   │   │   │   ├── subscription_model.py
│   │   │   │   │   ├── payment_model.py
│   │   │   │   │   ├── instagram_tracking_model.py
│   │   │   │   │   ├── audience_tracking_model.py
│   │   │   │   │   ├── referral_model.py
│   │   │   │   │   └── notification_model.py
│   │   │   │   ├── repositories/               # Repository implementations
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user_repository.py
│   │   │   │   │   ├── subscription_repository.py
│   │   │   │   │   ├── payment_repository.py
│   │   │   │   │   ├── instagram_request_repository.py
│   │   │   │   │   ├── content_tracking_repository.py
│   │   │   │   │   ├── audience_tracking_repository.py
│   │   │   │   │   ├── referral_repository.py
│   │   │   │   │   └── notification_repository.py
│   │   │   │   └── mappers/                    # Domain <-> ORM mappers
│   │   │   │       ├── __init__.py
│   │   │   │       ├── user_mapper.py
│   │   │   │       ├── subscription_mapper.py
│   │   │   │       ├── payment_mapper.py
│   │   │   │       ├── tracking_mapper.py
│   │   │   │       ├── referral_mapper.py
│   │   │   │       └── notification_mapper.py
│   │   │   └── migrations/                     # Alembic migrations
│   │   │       └── versions/
│   │   │
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── redis_cache.py                  # Redis cache implementation
│   │   │   └── in_memory_cache.py              # In-memory fallback
│   │   │
│   │   ├── external_services/
│   │   │   ├── __init__.py
│   │   │   ├── instagram/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── hikerapi_client.py          # HikerAPI adapter
│   │   │   │   └── instagram_api_adapter.py    # IInstagramAPIClient impl
│   │   │   ├── payment_gateways/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── telegram_stars_gateway.py
│   │   │   │   ├── robokassa_gateway.py
│   │   │   │   └── crypto_bot_gateway.py
│   │   │   └── telegram/
│   │   │       ├── __init__.py
│   │   │       └── telegram_notification_service.py
│   │   │
│   │   ├── messaging/
│   │   │   ├── __init__.py
│   │   │   ├── event_bus.py                    # Event bus implementation
│   │   │   └── event_handlers/
│   │   │       ├── __init__.py
│   │   │       ├── subscription_event_handlers.py
│   │   │       ├── payment_event_handlers.py
│   │   │       ├── tracking_event_handlers.py
│   │   │       └── referral_event_handlers.py
│   │   │
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   └── logger.py
│   │   │
│   │   └── config/
│   │       ├── __init__.py
│   │       ├── settings.py                     # Application settings
│   │       └── dependency_injection.py         # DI container
│   │
│   └── presentation/                           # PRESENTATION LAYER
│       ├── __init__.py
│       ├── telegram/
│       │   ├── __init__.py
│       │   ├── bot.py                          # Bot entry point
│       │   ├── handlers/                       # Thin handlers
│       │   │   ├── __init__.py
│       │   │   ├── start_handler.py
│       │   │   ├── subscription_handler.py
│       │   │   ├── payment_handler.py
│       │   │   ├── instagram_handler.py
│       │   │   ├── tracking_handler.py
│       │   │   ├── referral_handler.py
│       │   │   └── support_handler.py
│       │   ├── keyboards/
│       │   │   ├── __init__.py
│       │   │   ├── main_keyboard.py
│       │   │   ├── subscription_keyboard.py
│       │   │   ├── payment_keyboard.py
│       │   │   └── tracking_keyboard.py
│       │   ├── formatters/
│       │   │   ├── __init__.py
│       │   │   ├── user_formatter.py
│       │   │   ├── subscription_formatter.py
│       │   │   ├── payment_formatter.py
│       │   │   └── tracking_formatter.py
│       │   └── middleware/
│       │       ├── __init__.py
│       │       ├── auth_middleware.py
│       │       ├── rate_limit_middleware.py
│       │       └── logging_middleware.py
│       │
│       └── cli/                                # CLI interface (optional)
│           ├── __init__.py
│           └── commands.py
│
├── tests/                                      # TESTS
│   ├── __init__.py
│   ├── unit/                                   # Unit tests
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── user_management/
│   │   │   ├── subscription/
│   │   │   ├── payment/
│   │   │   ├── instagram_integration/
│   │   │   ├── content_tracking/
│   │   │   ├── audience_tracking/
│   │   │   ├── referral/
│   │   │   └── notification/
│   │   └── application/
│   │       ├── __init__.py
│   │       ├── user_management/
│   │       ├── subscription/
│   │       ├── payment/
│   │       └── ...
│   │
│   ├── integration/                            # Integration tests
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   ├── external_services/
│   │   └── use_cases/
│   │
│   ├── e2e/                                    # End-to-end tests
│   │   ├── __init__.py
│   │   └── telegram_bot/
│   │
│   └── fixtures/
│       ├── __init__.py
│       ├── domain_fixtures.py
│       └── infrastructure_fixtures.py
│
├── alembic/                                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── docs/                                       # Documentation
│   ├── architecture/
│   │   ├── bounded_contexts.md
│   │   ├── domain_model.md
│   │   └── infrastructure.md
│   ├── use_cases/
│   └── api/
│
├── scripts/                                    # Utility scripts
│   ├── migrate_data.py
│   └── seed_data.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── REFACTORING_MASTER_PLAN.md                  # This file
```

---

## 5. ПОШАГОВЫЙ ПЛАН МИГРАЦИИ

### Фаза 0: Подготовка (1-2 дня)


#### Шаг 0.1: Создание структуры проекта
- [ ] Создать папку `bobobot_inst_ddd/`
- [ ] Создать базовую структуру директорий
- [ ] Настроить `pyproject.toml` с зависимостями
- [ ] Настроить линтеры (ruff, mypy, black)
- [ ] Настроить pre-commit hooks

#### Шаг 0.2: Настройка инфраструктуры
- [ ] Настроить Docker Compose для разработки
- [ ] Настроить PostgreSQL
- [ ] Настроить Redis
- [ ] Настроить Alembic для миграций
- [ ] Создать базовую конфигурацию (settings.py)

#### Шаг 0.3: Настройка тестирования
- [ ] Настроить pytest
- [ ] Настроить coverage
- [ ] Создать базовые фикстуры
- [ ] Настроить CI/CD pipeline

---

### Фаза 1: Shared Kernel (3-4 дня)

#### Шаг 1.1: Базовые абстракции
- [ ] Создать `BaseValueObject` с методами equality, hash
- [ ] Создать `BaseEntity` с ID и equality по ID
- [ ] Создать `AggregateRoot` с domain events
- [ ] Создать `DomainEvent` базовый класс
- [ ] Создать `DomainException` базовый класс

**Тесты:**
- [ ] Unit тесты для BaseValueObject
- [ ] Unit тесты для BaseEntity
- [ ] Unit тесты для AggregateRoot
- [ ] Unit тесты для domain events

#### Шаг 1.2: Общие Value Objects
- [ ] Создать `Identifier` базовый класс для ID
- [ ] Создать `Money` VO (amount, currency)
- [ ] Создать `DateRange` VO (start, end)
- [ ] Создать `Email` VO с валидацией
- [ ] Создать `PhoneNumber` VO с валидацией

**Тесты:**
- [ ] Unit тесты для каждого VO
- [ ] Тесты валидации
- [ ] Тесты immutability

#### Шаг 1.3: Event Dispatcher
- [ ] Создать `EventDispatcher` для публикации событий
- [ ] Создать `EventHandler` интерфейс
- [ ] Реализовать in-memory event bus
- [ ] Добавить логирование событий

**Тесты:**
- [ ] Unit тесты для EventDispatcher
- [ ] Integration тесты для event flow

#### Шаг 1.4: Specification Pattern
- [ ] Создать `Specification` базовый класс
- [ ] Реализовать `AndSpecification`, `OrSpecification`, `NotSpecification`
- [ ] Примеры использования

**Тесты:**
- [ ] Unit тесты для Specification
- [ ] Тесты композиции спецификаций

---

### Фаза 2: User Management Context (4-5 дней)

#### Шаг 2.1: Domain Layer
- [ ] Создать `UserId` VO
- [ ] Создать `TelegramId` VO с валидацией
- [ ] Создать `Username` VO
- [ ] Создать `Profile` VO (first_name, last_name)
- [ ] Создать `Language` VO (enum: ru, en)
- [ ] Создать `User` aggregate с методами:
  - `register()` - регистрация
  - `updateProfile()` - обновление профиля
  - `changeLanguage()` - смена языка
- [ ] Создать domain events:
  - `UserRegistered`
  - `UserProfileUpdated`
  - `UserLanguageChanged`
- [ ] Создать domain exceptions:
  - `UserNotFoundException`
  - `InvalidTelegramIdException`
- [ ] Создать `IUserRepository` интерфейс

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для User aggregate
- [ ] Тесты бизнес-правил
- [ ] Тесты domain events

#### Шаг 2.2: Application Layer
- [ ] Создать DTOs:
  - `UserDTO`
  - `UserProfileDTO`
- [ ] Создать Commands:
  - `RegisterUserCommand`
  - `UpdateUserProfileCommand`
- [ ] Создать Queries:
  - `GetUserByTelegramIdQuery`
  - `GetUserByIdQuery`
- [ ] Создать Use Cases:
  - `RegisterUserUseCase`
  - `UpdateUserProfileUseCase`
  - `GetUserByTelegramIdUseCase`

**Тесты:**
- [ ] Unit тесты для use cases (с моками)
- [ ] Integration тесты для use cases

#### Шаг 2.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модель `UserModel`
- [ ] Создать `UserMapper` (domain <-> ORM)
- [ ] Реализовать `UserRepository` (SQLAlchemy)
- [ ] Создать Alembic миграцию для users таблицы

**Тесты:**
- [ ] Integration тесты для UserRepository
- [ ] Тесты маппинга

#### Шаг 2.4: Presentation Layer
- [ ] Создать `StartHandler` (тонкий контроллер)
- [ ] Создать `UserFormatter` для форматирования ответов
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для /start команды

---

### Фаза 3: Subscription Context (5-6 дней)

#### Шаг 3.1: Domain Layer
- [ ] Создать Value Objects:
  - `SubscriptionId`
  - `SubscriptionType` (enum: FREE, PAID)
  - `Period` (start_date, end_date)
  - `Duration` (days)
  - `Pricing` (stars, rub, ton, usdt)
  - `SubscriptionStatus` (enum)
- [ ] Создать `Subscription` aggregate с методами:
  - `activate()` - активация
  - `extend(days)` - продление
  - `cancel()` - отмена
  - `isExpired()` - проверка истечения
  - `getRemainingDays()` - оставшиеся дни
- [ ] Создать `SubscriptionPlan` entity
- [ ] Создать domain events:
  - `SubscriptionActivated`
  - `SubscriptionExtended`
  - `SubscriptionExpired`
  - `SubscriptionCancelled`
  - `TrialSubscriptionCreated`
- [ ] Создать domain services:
  - `SubscriptionExpirationService`
  - `SubscriptionPricingService`
- [ ] Создать domain exceptions:
  - `SubscriptionNotFoundException`
  - `SubscriptionAlreadyActiveException`
  - `SubscriptionExpiredException`
- [ ] Создать repository interfaces:
  - `ISubscriptionRepository`
  - `ISubscriptionPlanRepository`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для Subscription aggregate
- [ ] Тесты бизнес-правил (истечение, продление)
- [ ] Тесты domain services
- [ ] Тесты domain events

#### Шаг 3.2: Application Layer
- [ ] Создать DTOs:
  - `SubscriptionDTO`
  - `SubscriptionPlanDTO`
- [ ] Создать Commands:
  - `ActivateSubscriptionCommand`
  - `ExtendSubscriptionCommand`
  - `CancelSubscriptionCommand`
  - `CreateTrialSubscriptionCommand`
- [ ] Создать Queries:
  - `GetActiveSubscriptionQuery`
  - `GetSubscriptionStatusQuery`
  - `GetAvailablePlansQuery`
- [ ] Создать Use Cases:
  - `ActivateSubscriptionUseCase`
  - `ExtendSubscriptionUseCase`
  - `CancelSubscriptionUseCase`
  - `CheckSubscriptionStatusUseCase`
  - `CreateTrialSubscriptionUseCase`
  - `GetAvailablePlansUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 3.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модели:
  - `SubscriptionModel`
  - `SubscriptionPlanModel`
- [ ] Создать mappers
- [ ] Реализовать repositories
- [ ] Создать Alembic миграции

**Тесты:**
- [ ] Integration тесты для repositories
- [ ] Тесты маппинга

#### Шаг 3.4: Presentation Layer
- [ ] Создать `SubscriptionHandler`
- [ ] Создать `SubscriptionFormatter`
- [ ] Создать keyboards для подписок
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для subscription flow

---

### Фаза 4: Payment Context (6-7 дней)


#### Шаг 4.1: Domain Layer
- [ ] Создать Value Objects:
  - `PaymentId`
  - `InvoiceId`
  - `Amount` (с валидацией > 0)
  - `Currency` (enum: XTR, RUB, TON, USDT)
  - `PaymentMethod` (enum: TELEGRAM_STARS, ROBOKASSA, CRYPTO_BOT)
  - `PaymentStatus` (enum: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED, REFUNDED)
  - `ProviderPaymentId`
- [ ] Создать `Payment` aggregate с методами:
  - `process()` - начать обработку
  - `complete()` - завершить успешно
  - `fail()` - провалить
  - `refund()` - вернуть деньги
  - `canBeRefunded()` - можно ли вернуть
- [ ] Создать `Invoice` entity
- [ ] Создать domain events:
  - `PaymentCreated`
  - `PaymentProcessing`
  - `PaymentCompleted`
  - `PaymentFailed`
  - `PaymentRefunded`
- [ ] Создать domain services:
  - `PaymentProcessingService`
  - `InvoiceGenerationService`
- [ ] Создать domain exceptions:
  - `PaymentNotFoundException`
  - `InvalidAmountException`
  - `PaymentAlreadyProcessedException`
- [ ] Создать repository interface:
  - `IPaymentRepository`
- [ ] Создать port interfaces:
  - `ITelegramStarsPaymentGateway`
  - `IRobokassaPaymentGateway`
  - `ICryptoBotPaymentGateway`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для Payment aggregate
- [ ] Тесты бизнес-правил (refund logic)
- [ ] Тесты domain services
- [ ] Тесты domain events

#### Шаг 4.2: Application Layer
- [ ] Создать DTOs:
  - `PaymentDTO`
  - `InvoiceDTO`
- [ ] Создать Commands:
  - `CreatePaymentCommand`
  - `ProcessPaymentCommand`
  - `CompletePaymentCommand`
  - `RefundPaymentCommand`
- [ ] Создать Queries:
  - `GetPaymentStatusQuery`
  - `GetUserPaymentsQuery`
- [ ] Создать Use Cases:
  - `CreatePaymentUseCase`
  - `ProcessPaymentUseCase`
  - `CompletePaymentUseCase`
  - `RefundPaymentUseCase`
  - `GetPaymentStatusUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 4.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модель `PaymentModel`
- [ ] Создать mapper
- [ ] Реализовать `PaymentRepository`
- [ ] Реализовать payment gateway adapters:
  - `TelegramStarsGateway`
  - `RobokassaGateway`
  - `CryptoBotGateway`
- [ ] Создать Alembic миграцию

**Тесты:**
- [ ] Integration тесты для PaymentRepository
- [ ] Integration тесты для payment gateways (с моками)
- [ ] Тесты маппинга

#### Шаг 4.4: Presentation Layer
- [ ] Создать `PaymentHandler`
- [ ] Создать `PaymentFormatter`
- [ ] Создать keyboards для платежей
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для payment flow

#### Шаг 4.5: Event Handlers
- [ ] Создать event handler для `PaymentCompleted`:
  - Активировать/продлить подписку
  - Начислить реферальную награду
  - Отправить уведомление

**Тесты:**
- [ ] Integration тесты для event handlers

---

### Фаза 5: Instagram Integration Context (5-6 дней)

#### Шаг 5.1: Domain Layer
- [ ] Создать Value Objects:
  - `InstagramUsername`
  - `InstagramUserId`
  - `ProfileStatistics` (followers, following, posts)
  - `Bio`
  - `ProfilePicture`
  - `RequestType` (enum)
- [ ] Создать `InstagramProfile` aggregate с методами:
  - `updateStatistics()`
  - `isPrivate()`
- [ ] Создать `InstagramRequest` entity
- [ ] Создать domain events:
  - `ProfileDataFetched`
  - `ProfileNotFound`
  - `ProfileIsPrivate`
  - `RateLimitExceeded`
- [ ] Создать domain services:
  - `RateLimitingService`
  - `CacheService`
- [ ] Создать domain exceptions:
  - `ProfileNotFoundException`
  - `PrivateProfileException`
  - `RateLimitExceededException`
- [ ] Создать repository interface:
  - `IInstagramRequestRepository`
- [ ] Создать port interface:
  - `IInstagramAPIClient`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для InstagramProfile aggregate
- [ ] Тесты domain services
- [ ] Тесты domain events

#### Шаг 5.2: Application Layer
- [ ] Создать DTOs:
  - `InstagramProfileDTO`
  - `InstagramContentDTO`
- [ ] Создать Commands:
  - `FetchInstagramProfileCommand`
- [ ] Создать Queries:
  - `GetInstagramProfileQuery`
  - `GetInstagramStoriesQuery`
  - `GetInstagramPostsQuery`
  - `SearchInstagramUsersQuery`
- [ ] Создать Use Cases:
  - `FetchInstagramProfileUseCase`
  - `FetchInstagramStoriesUseCase`
  - `FetchInstagramPostsUseCase`
  - `FetchInstagramReelsUseCase`
  - `SearchInstagramUsersUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 5.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модель `InstagramRequestModel`
- [ ] Создать mapper
- [ ] Реализовать `InstagramRequestRepository`
- [ ] Реализовать `HikerAPIAdapter` (IInstagramAPIClient)
- [ ] Реализовать `RedisCacheService`
- [ ] Создать Alembic миграцию

**Тесты:**
- [ ] Integration тесты для repository
- [ ] Integration тесты для HikerAPI adapter (с моками)
- [ ] Тесты кэширования

#### Шаг 5.4: Presentation Layer
- [ ] Создать `InstagramHandler`
- [ ] Создать `InstagramFormatter`
- [ ] Создать keyboards для Instagram
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для Instagram flow

---

### Фаза 6: Content Tracking Context (6-7 дней)

#### Шаг 6.1: Domain Layer
- [ ] Создать Value Objects:
  - `TrackingId`
  - `TargetProfile` (username, user_id)
  - `TrackingSettings` (types, intervals)
  - `ContentType` (enum: STORY, POST, REEL)
  - `CheckInterval` (enum: 1h, 6h, 12h, 24h)
  - `TrackingStatus` (enum: ACTIVE, PAUSED, CANCELLED)
- [ ] Создать `ContentTracking` aggregate с методами:
  - `activate()`
  - `deactivate()`
  - `updateSettings()`
  - `shouldCheck()` - нужна ли проверка
- [ ] Создать `TrackedContent` entity
- [ ] Создать domain events:
  - `TrackingActivated`
  - `TrackingDeactivated`
  - `NewContentDetected`
  - `TrackingCheckCompleted`
  - `TrackingCheckFailed`
- [ ] Создать domain services:
  - `ContentDetectionService`
  - `TrackingSchedulerService`
- [ ] Создать domain exceptions:
  - `TrackingNotFoundException`
  - `TrackingAlreadyExistsException`
- [ ] Создать repository interfaces:
  - `IContentTrackingRepository`
  - `ITrackedContentRepository`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для ContentTracking aggregate
- [ ] Тесты бизнес-правил
- [ ] Тесты domain services
- [ ] Тесты domain events

#### Шаг 6.2: Application Layer
- [ ] Создать DTOs:
  - `ContentTrackingDTO`
  - `TrackedContentDTO`
- [ ] Создать Commands:
  - `ActivateContentTrackingCommand`
  - `DeactivateContentTrackingCommand`
  - `UpdateTrackingSettingsCommand`
- [ ] Создать Queries:
  - `GetUserTrackingsQuery`
  - `GetTrackingStatusQuery`
- [ ] Создать Use Cases:
  - `ActivateContentTrackingUseCase`
  - `DeactivateContentTrackingUseCase`
  - `UpdateTrackingSettingsUseCase`
  - `CheckTrackingUpdatesUseCase`
  - `GetUserTrackingsUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 6.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модели:
  - `ContentTrackingModel`
  - `TrackedContentModel`
- [ ] Создать mappers
- [ ] Реализовать repositories
- [ ] Создать Alembic миграции

**Тесты:**
- [ ] Integration тесты для repositories
- [ ] Тесты маппинга

#### Шаг 6.4: Presentation Layer
- [ ] Создать `TrackingHandler`
- [ ] Создать `TrackingFormatter`
- [ ] Создать keyboards для tracking
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для tracking flow

#### Шаг 6.5: Background Jobs
- [ ] Создать scheduled job для проверки обновлений
- [ ] Интегрировать с event bus

**Тесты:**
- [ ] Integration тесты для background jobs

---

### Фаза 7: Audience Tracking Context (5-6 дней)


#### Шаг 7.1: Domain Layer
- [ ] Создать Value Objects:
  - `AudienceTrackingId`
  - `AudienceSubscription` (expires_at, is_active)
  - `AudienceSnapshot` (followers_count, following_count)
  - `FollowerLimit` (100,000)
  - `AudienceChangeType` (enum: NEW_FOLLOWER, UNFOLLOWED, etc.)
  - `AudiencePricing` (576 followers + 129 RUB/month)
- [ ] Создать `AudienceTracking` aggregate с методами:
  - `activate()`
  - `deactivate()`
  - `updateSnapshot()`
  - `detectChanges()`
  - `isExpired()`
- [ ] Создать `AudienceChange` entity
- [ ] Создать domain events:
  - `AudienceTrackingActivated`
  - `AudienceTrackingExpired`
  - `NewFollowerDetected`
  - `UnfollowDetected`
  - `FollowerLimitExceeded`
- [ ] Создать domain services:
  - `AudienceComparisonService`
  - `AudiencePricingService`
- [ ] Создать domain exceptions:
  - `FollowerLimitExceededException`
  - `AudienceTrackingExpiredException`
- [ ] Создать repository interfaces:
  - `IAudienceTrackingRepository`
  - `IAudienceChangeRepository`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для AudienceTracking aggregate
- [ ] Тесты бизнес-правил (лимит 100k)
- [ ] Тесты domain services
- [ ] Тесты domain events

#### Шаг 7.2: Application Layer
- [ ] Создать DTOs:
  - `AudienceTrackingDTO`
  - `AudienceChangeDTO`
- [ ] Создать Commands:
  - `ActivateAudienceTrackingCommand`
  - `DeactivateAudienceTrackingCommand`
- [ ] Создать Queries:
  - `GetAudienceTrackingStatusQuery`
  - `CalculateAudienceTrackingPriceQuery`
- [ ] Создать Use Cases:
  - `ActivateAudienceTrackingUseCase`
  - `DeactivateAudienceTrackingUseCase`
  - `CheckAudienceChangesUseCase`
  - `GetAudienceTrackingStatusUseCase`
  - `CalculateAudienceTrackingPriceUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 7.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модели:
  - `AudienceTrackingModel`
  - `AudienceChangeModel`
- [ ] Создать mappers
- [ ] Реализовать repositories
- [ ] Создать Alembic миграции

**Тесты:**
- [ ] Integration тесты для repositories
- [ ] Тесты маппинга

#### Шаг 7.4: Presentation Layer
- [ ] Создать handlers для audience tracking
- [ ] Создать formatters
- [ ] Создать keyboards
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для audience tracking flow

---

### Фаза 8: Referral Context (4-5 дней)

#### Шаг 8.1: Domain Layer
- [ ] Создать Value Objects:
  - `ReferralId`
  - `ReferralCode`
  - `CommissionRate` (5%)
  - `Rewards` (usdt, ton, stars, rub)
  - `ReferralStatus` (enum)
- [ ] Создать `Referral` aggregate с методами:
  - `activate()`
  - `grantReward()`
  - `calculateCommission()`
- [ ] Создать `ReferralStats` entity
- [ ] Создать domain events:
  - `ReferralCreated`
  - `ReferralActivated`
  - `ReferralRewardGranted`
  - `ReferralPaymentReceived`
- [ ] Создать domain services:
  - `ReferralCommissionService`
  - `ReferralLinkGenerationService`
- [ ] Создать domain exceptions:
  - `ReferralNotFoundException`
  - `InvalidReferralCodeException`
- [ ] Создать repository interfaces:
  - `IReferralRepository`
  - `IReferralStatsRepository`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для Referral aggregate
- [ ] Тесты бизнес-правил (5% комиссия)
- [ ] Тесты domain services
- [ ] Тесты domain events

#### Шаг 8.2: Application Layer
- [ ] Создать DTOs:
  - `ReferralDTO`
  - `ReferralStatsDTO`
- [ ] Создать Commands:
  - `CreateReferralCommand`
  - `ApplyReferralCodeCommand`
  - `GrantReferralRewardCommand`
- [ ] Создать Queries:
  - `GetReferralStatsQuery`
  - `GenerateReferralLinkQuery`
- [ ] Создать Use Cases:
  - `CreateReferralUseCase`
  - `ApplyReferralCodeUseCase`
  - `GrantReferralRewardUseCase`
  - `GetReferralStatsUseCase`
  - `GenerateReferralLinkUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 8.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модели:
  - `ReferralModel`
  - `ReferralStatsModel`
- [ ] Создать mappers
- [ ] Реализовать repositories
- [ ] Создать Alembic миграции

**Тесты:**
- [ ] Integration тесты для repositories
- [ ] Тесты маппинга

#### Шаг 8.4: Presentation Layer
- [ ] Создать `ReferralHandler`
- [ ] Создать `ReferralFormatter`
- [ ] Создать keyboards
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] E2E тесты для referral flow

#### Шаг 8.5: Event Handlers
- [ ] Создать event handler для `PaymentCompleted`:
  - Начислить реферальную награду

**Тесты:**
- [ ] Integration тесты для event handlers

---

### Фаза 9: Notification Context (3-4 дня)

#### Шаг 9.1: Domain Layer
- [ ] Создать Value Objects:
  - `NotificationId`
  - `NotificationType` (enum)
  - `NotificationContent` (text, media, keyboard)
  - `NotificationStatus` (enum)
- [ ] Создать `Notification` aggregate с методами:
  - `send()`
  - `markAsRead()`
  - `retry()`
- [ ] Создать domain events:
  - `NotificationCreated`
  - `NotificationSent`
  - `NotificationFailed`
  - `NotificationRead`
- [ ] Создать domain exceptions:
  - `NotificationSendFailedException`
- [ ] Создать repository interface:
  - `INotificationRepository`
- [ ] Создать port interface:
  - `ITelegramNotificationService`

**Тесты:**
- [ ] Unit тесты для всех VO
- [ ] Unit тесты для Notification aggregate
- [ ] Тесты domain events

#### Шаг 9.2: Application Layer
- [ ] Создать DTOs:
  - `NotificationDTO`
- [ ] Создать Commands:
  - `SendNotificationCommand`
  - `SendBulkNotificationsCommand`
- [ ] Создать Queries:
  - `GetNotificationStatusQuery`
- [ ] Создать Use Cases:
  - `SendNotificationUseCase`
  - `SendBulkNotificationsUseCase`
  - `RetryFailedNotificationsUseCase`

**Тесты:**
- [ ] Unit тесты для use cases
- [ ] Integration тесты

#### Шаг 9.3: Infrastructure Layer
- [ ] Создать SQLAlchemy модель `NotificationModel`
- [ ] Создать mapper
- [ ] Реализовать `NotificationRepository`
- [ ] Реализовать `TelegramNotificationService`
- [ ] Создать Alembic миграцию

**Тесты:**
- [ ] Integration тесты для repository
- [ ] Integration тесты для notification service

#### Шаг 9.4: Event Handlers
- [ ] Создать event handlers для всех доменных событий:
  - `NewContentDetected` → отправить уведомление
  - `SubscriptionExpired` → отправить уведомление
  - `PaymentCompleted` → отправить уведомление
  - и т.д.

**Тесты:**
- [ ] Integration тесты для event handlers

---

### Фаза 10: Unit of Work & Dependency Injection (3-4 дня)

#### Шаг 10.1: Unit of Work
- [ ] Создать `IUnitOfWork` интерфейс
- [ ] Реализовать `SQLAlchemyUnitOfWork`
- [ ] Интегрировать UoW во все use cases
- [ ] Добавить транзакционность

**Тесты:**
- [ ] Integration тесты для UoW
- [ ] Тесты rollback при ошибках

#### Шаг 10.2: Dependency Injection
- [ ] Настроить DI контейнер (dependency-injector или punq)
- [ ] Зарегистрировать все зависимости
- [ ] Настроить lifetimes (singleton, scoped, transient)
- [ ] Интегрировать с Telegram Bot

**Тесты:**
- [ ] Тесты DI контейнера

---

### Фаза 11: Миграция данных (2-3 дня)

#### Шаг 11.1: Скрипты миграции
- [ ] Создать скрипт миграции пользователей
- [ ] Создать скрипт миграции подписок
- [ ] Создать скрипт миграции платежей
- [ ] Создать скрипт миграции отслеживаний
- [ ] Создать скрипт миграции рефералов

#### Шаг 11.2: Валидация данных
- [ ] Проверить целостность данных
- [ ] Проверить корректность маппинга
- [ ] Создать отчет о миграции

**Тесты:**
- [ ] Integration тесты для миграции

---

### Фаза 12: Интеграция и тестирование (4-5 дней)

#### Шаг 12.1: E2E тесты
- [ ] E2E тесты для всех user flows
- [ ] E2E тесты для payment flows
- [ ] E2E тесты для tracking flows
- [ ] E2E тесты для referral flows

#### Шаг 12.2: Performance тесты
- [ ] Load тесты для критичных use cases
- [ ] Stress тесты для базы данных
- [ ] Оптимизация запросов

#### Шаг 12.3: Security тесты
- [ ] Проверка валидации входных данных
- [ ] Проверка авторизации
- [ ] Проверка SQL injection
- [ ] Проверка XSS

---

### Фаза 13: Документация и деплой (2-3 дня)

#### Шаг 13.1: Документация
- [ ] Документация архитектуры
- [ ] Документация bounded contexts
- [ ] Документация use cases
- [ ] API документация
- [ ] README для разработчиков

#### Шаг 13.2: Деплой
- [ ] Настроить production окружение
- [ ] Настроить мониторинг
- [ ] Настроить логирование
- [ ] Настроить алерты
- [ ] Выполнить деплой

---

## 6. ПАТТЕРНЫ ПРОЕКТИРОВАНИЯ


### 6.1 Repository Pattern

**Цель:** Абстракция доступа к данным, изоляция домена от инфраструктуры

**Реализация:**
```python
# Domain Layer - Interface
class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_telegram_id(self, telegram_id: TelegramId) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    def delete(self, user_id: UserId) -> None:
        pass

# Infrastructure Layer - Implementation
class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def get_by_id(self, user_id: UserId) -> Optional[User]:
        model = self._session.query(UserModel).filter_by(id=user_id.value).first()
        return UserMapper.to_domain(model) if model else None
    
    def save(self, user: User) -> None:
        model = UserMapper.to_orm(user)
        self._session.merge(model)
```

**Преимущества:**
- Домен не зависит от БД
- Легко тестировать (моки)
- Легко менять БД

---

### 6.2 Unit of Work Pattern

**Цель:** Управление транзакциями, координация изменений

**Реализация:**
```python
# Application Layer - Interface
class IUnitOfWork(ABC):
    users: IUserRepository
    subscriptions: ISubscriptionRepository
    payments: IPaymentRepository
    
    @abstractmethod
    def __enter__(self):
        pass
    
    @abstractmethod
    def __exit__(self, *args):
        pass
    
    @abstractmethod
    def commit(self) -> None:
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        pass

# Infrastructure Layer - Implementation
class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory
    
    def __enter__(self):
        self._session = self._session_factory()
        self.users = SQLAlchemyUserRepository(self._session)
        self.subscriptions = SQLAlchemySubscriptionRepository(self._session)
        self.payments = SQLAlchemyPaymentRepository(self._session)
        return self
    
    def __exit__(self, *args):
        self.rollback()
        self._session.close()
    
    def commit(self):
        self._session.commit()
    
    def rollback(self):
        self._session.rollback()

# Use Case
class ActivateSubscriptionUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow
    
    def execute(self, command: ActivateSubscriptionCommand) -> Result:
        with self._uow:
            user = self._uow.users.get_by_id(command.user_id)
            subscription = Subscription.activate(user.id, command.plan)
            self._uow.subscriptions.save(subscription)
            self._uow.commit()
            return Result.success(subscription)
```

**Преимущества:**
- Атомарность операций
- Централизованное управление транзакциями
- Легко откатить изменения

---

### 6.3 Aggregate Pattern

**Цель:** Обеспечение консистентности данных, инкапсуляция бизнес-логики

**Реализация:**
```python
class Subscription(AggregateRoot):
    def __init__(
        self,
        subscription_id: SubscriptionId,
        user_id: UserId,
        subscription_type: SubscriptionType,
        period: Period,
        status: SubscriptionStatus
    ):
        super().__init__(subscription_id)
        self._user_id = user_id
        self._subscription_type = subscription_type
        self._period = period
        self._status = status
    
    @staticmethod
    def activate(user_id: UserId, plan: SubscriptionPlan) -> 'Subscription':
        """Factory method для создания подписки"""
        subscription_id = SubscriptionId.generate()
        period = Period.from_duration(plan.duration)
        subscription = Subscription(
            subscription_id,
            user_id,
            SubscriptionType.PAID,
            period,
            SubscriptionStatus.ACTIVE
        )
        subscription.add_domain_event(SubscriptionActivated(subscription_id, user_id))
        return subscription
    
    def extend(self, days: int) -> None:
        """Продление подписки"""
        if self.is_expired():
            raise SubscriptionExpiredException()
        
        self._period = self._period.extend(days)
        self.add_domain_event(SubscriptionExtended(self.id, days))
    
    def cancel(self) -> None:
        """Отмена подписки"""
        self._status = SubscriptionStatus.CANCELLED
        self.add_domain_event(SubscriptionCancelled(self.id))
    
    def is_expired(self) -> bool:
        """Проверка истечения"""
        return self._period.is_expired()
    
    # Invariants
    def _validate(self):
        if self._status == SubscriptionStatus.ACTIVE and self.is_expired():
            raise DomainException("Active subscription cannot be expired")
```

**Преимущества:**
- Бизнес-логика в домене
- Гарантия консистентности
- Четкие границы транзакций

---

### 6.4 Value Object Pattern

**Цель:** Неизменяемые объекты значений, валидация

**Реализация:**
```python
@dataclass(frozen=True)
class Amount(BaseValueObject):
    value: Decimal
    
    def __post_init__(self):
        if self.value <= 0:
            raise InvalidAmountException("Amount must be positive")
    
    def add(self, other: 'Amount') -> 'Amount':
        return Amount(self.value + other.value)
    
    def multiply(self, factor: Decimal) -> 'Amount':
        return Amount(self.value * factor)
    
    def __str__(self) -> str:
        return f"{self.value:.2f}"

@dataclass(frozen=True)
class Currency(BaseValueObject):
    code: str
    
    def __post_init__(self):
        if self.code not in ['XTR', 'RUB', 'TON', 'USDT']:
            raise InvalidCurrencyException(f"Invalid currency: {self.code}")

@dataclass(frozen=True)
class Money(BaseValueObject):
    amount: Amount
    currency: Currency
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchException()
        return Money(self.amount.add(other.amount), self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount} {self.currency.code}"
```

**Преимущества:**
- Валидация в конструкторе
- Immutability
- Семантическая ясность

---

### 6.5 Domain Events Pattern

**Цель:** Асинхронная коммуникация между контекстами

**Реализация:**
```python
# Domain Event
@dataclass(frozen=True)
class PaymentCompleted(DomainEvent):
    payment_id: PaymentId
    user_id: UserId
    amount: Money
    subscription_days: int
    occurred_at: datetime = field(default_factory=datetime.utcnow)

# Aggregate Root
class Payment(AggregateRoot):
    def complete(self) -> None:
        if self._status != PaymentStatus.PROCESSING:
            raise PaymentAlreadyProcessedException()
        
        self._status = PaymentStatus.COMPLETED
        self._paid_at = datetime.utcnow()
        
        # Publish domain event
        self.add_domain_event(PaymentCompleted(
            self.id,
            self._user_id,
            self._amount,
            self._subscription_days
        ))

# Event Handler (Infrastructure)
class PaymentCompletedHandler:
    def __init__(
        self,
        subscription_use_case: ExtendSubscriptionUseCase,
        referral_use_case: GrantReferralRewardUseCase,
        notification_use_case: SendNotificationUseCase
    ):
        self._subscription_use_case = subscription_use_case
        self._referral_use_case = referral_use_case
        self._notification_use_case = notification_use_case
    
    def handle(self, event: PaymentCompleted) -> None:
        # Extend subscription
        self._subscription_use_case.execute(
            ExtendSubscriptionCommand(event.user_id, event.subscription_days)
        )
        
        # Grant referral reward
        self._referral_use_case.execute(
            GrantReferralRewardCommand(event.user_id, event.amount)
        )
        
        # Send notification
        self._notification_use_case.execute(
            SendNotificationCommand(
                event.user_id,
                NotificationType.PAYMENT_SUCCESS,
                f"Payment completed: {event.amount}"
            )
        )
```

**Преимущества:**
- Слабая связанность
- Асинхронность
- Легко добавлять новые обработчики

---

### 6.6 Specification Pattern

**Цель:** Инкапсуляция бизнес-правил, переиспользование

**Реализация:**
```python
class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        pass
    
    def and_(self, other: 'Specification') -> 'Specification':
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification') -> 'Specification':
        return OrSpecification(self, other)
    
    def not_(self) -> 'Specification':
        return NotSpecification(self)

class ActiveSubscriptionSpecification(Specification):
    def is_satisfied_by(self, subscription: Subscription) -> bool:
        return subscription.status == SubscriptionStatus.ACTIVE and not subscription.is_expired()

class PaidSubscriptionSpecification(Specification):
    def is_satisfied_by(self, subscription: Subscription) -> bool:
        return subscription.subscription_type == SubscriptionType.PAID

# Usage
active_paid_spec = ActiveSubscriptionSpecification().and_(PaidSubscriptionSpecification())

if active_paid_spec.is_satisfied_by(subscription):
    # Allow access
    pass
```

**Преимущества:**
- Переиспользование правил
- Композиция правил
- Читаемость кода

---

### 6.7 Factory Pattern

**Цель:** Создание сложных объектов

**Реализация:**
```python
class SubscriptionFactory:
    @staticmethod
    def create_trial(user_id: UserId) -> Subscription:
        """Создание пробной подписки на 7 дней"""
        subscription_id = SubscriptionId.generate()
        period = Period.from_days(7)
        return Subscription(
            subscription_id,
            user_id,
            SubscriptionType.PAID,
            period,
            SubscriptionStatus.ACTIVE
        )
    
    @staticmethod
    def create_from_plan(user_id: UserId, plan: SubscriptionPlan) -> Subscription:
        """Создание подписки из тарифа"""
        subscription_id = SubscriptionId.generate()
        period = Period.from_duration(plan.duration)
        return Subscription(
            subscription_id,
            user_id,
            SubscriptionType.PAID,
            period,
            SubscriptionStatus.ACTIVE
        )
```

---

### 6.8 Strategy Pattern

**Цель:** Выбор алгоритма в runtime

**Реализация:**
```python
class PaymentGatewayStrategy(ABC):
    @abstractmethod
    async def process_payment(self, payment: Payment) -> PaymentResult:
        pass

class TelegramStarsStrategy(PaymentGatewayStrategy):
    async def process_payment(self, payment: Payment) -> PaymentResult:
        # Telegram Stars logic
        pass

class RobokassaStrategy(PaymentGatewayStrategy):
    async def process_payment(self, payment: Payment) -> PaymentResult:
        # Robokassa logic
        pass

class PaymentProcessor:
    def __init__(self):
        self._strategies = {
            PaymentMethod.TELEGRAM_STARS: TelegramStarsStrategy(),
            PaymentMethod.ROBOKASSA: RobokassaStrategy(),
            PaymentMethod.CRYPTO_BOT: CryptoBotStrategy()
        }
    
    async def process(self, payment: Payment) -> PaymentResult:
        strategy = self._strategies[payment.payment_method]
        return await strategy.process_payment(payment)
```

---

## 7. ТЕСТИРОВАНИЕ

### 7.1 Пирамида тестирования

```
        /\
       /  \
      / E2E\          10% - End-to-End тесты
     /______\
    /        \
   /Integration\     30% - Integration тесты
  /____________\
 /              \
/   Unit Tests   \   60% - Unit тесты
/__________________\
```

### 7.2 Unit тесты (Domain Layer)

**Цель:** Тестирование бизнес-логики в изоляции

**Пример:**
```python
class TestSubscription:
    def test_activate_subscription_creates_active_subscription(self):
        # Arrange
        user_id = UserId.generate()
        plan = SubscriptionPlan(
            PlanId.generate(),
            "7 days",
            Duration.from_days(7),
            Pricing(stars=50)
        )
        
        # Act
        subscription = Subscription.activate(user_id, plan)
        
        # Assert
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert not subscription.is_expired()
        assert len(subscription.domain_events) == 1
        assert isinstance(subscription.domain_events[0], SubscriptionActivated)
    
    def test_extend_expired_subscription_raises_exception(self):
        # Arrange
        subscription = create_expired_subscription()
        
        # Act & Assert
        with pytest.raises(SubscriptionExpiredException):
            subscription.extend(7)
    
    def test_cancel_subscription_changes_status(self):
        # Arrange
        subscription = create_active_subscription()
        
        # Act
        subscription.cancel()
        
        # Assert
        assert subscription.status == SubscriptionStatus.CANCELLED
        assert any(isinstance(e, SubscriptionCancelled) for e in subscription.domain_events)
```

### 7.3 Integration тесты (Application + Infrastructure)

**Цель:** Тестирование взаимодействия слоев

**Пример:**
```python
class TestActivateSubscriptionUseCase:
    @pytest.fixture
    def uow(self, db_session):
        return SQLAlchemyUnitOfWork(lambda: db_session)
    
    @pytest.fixture
    def use_case(self, uow):
        return ActivateSubscriptionUseCase(uow)
    
    def test_activate_subscription_saves_to_database(self, use_case, uow):
        # Arrange
        user = create_test_user()
        with uow:
            uow.users.save(user)
            uow.commit()
        
        command = ActivateSubscriptionCommand(
            user_id=user.id,
            plan_code="7_days"
        )
        
        # Act
        result = use_case.execute(command)
        
        # Assert
        assert result.is_success
        
        with uow:
            subscription = uow.subscriptions.get_by_user_id(user.id)
            assert subscription is not None
            assert subscription.status == SubscriptionStatus.ACTIVE
```

### 7.4 E2E тесты (Presentation Layer)

**Цель:** Тестирование полного user flow

**Пример:**
```python
class TestSubscriptionFlow:
    @pytest.fixture
    async def bot_client(self):
        return TelegramBotTestClient()
    
    async def test_user_can_activate_subscription(self, bot_client):
        # Arrange
        user_id = 12345
        
        # Act - Start bot
        response = await bot_client.send_command(user_id, "/start")
        assert "Добро пожаловать" in response.text
        
        # Act - Open tariffs
        response = await bot_client.click_button(user_id, "tariffs_menu")
        assert "Тарифы" in response.text
        
        # Act - Select plan
        response = await bot_client.click_button(user_id, "select_tariff_7_days")
        assert "Оплата" in response.text
        
        # Act - Complete payment (mock)
        await bot_client.complete_payment(user_id, invoice_id=123)
        
        # Assert - Check subscription
        response = await bot_client.send_command(user_id, "/subscription")
        assert "Активна" in response.text
```

### 7.5 Coverage цели

- **Domain Layer:** 100% coverage
- **Application Layer:** 90%+ coverage
- **Infrastructure Layer:** 80%+ coverage
- **Presentation Layer:** 70%+ coverage

---

## 8. МЕТРИКИ УСПЕХА

### 8.1 Технические метрики

#### Качество кода:
- [ ] Code coverage > 85%
- [ ] Cyclomatic complexity < 10
- [ ] Maintainability index > 70
- [ ] 0 critical bugs
- [ ] 0 security vulnerabilities

#### Производительность:
- [ ] API response time < 200ms (p95)
- [ ] Database query time < 50ms (p95)
- [ ] Memory usage < 512MB
- [ ] CPU usage < 50%

#### Архитектура:
- [ ] Все зависимости направлены к домену
- [ ] Нет циклических зависимостей
- [ ] Каждый bounded context изолирован
- [ ] Все use cases покрыты тестами

### 8.2 Бизнес-метрики

- [ ] 0 downtime при миграции
- [ ] Все существующие функции работают
- [ ] Время разработки новых фич сокращено на 40%
- [ ] Время исправления багов сокращено на 50%
- [ ] Onboarding новых разработчиков < 2 недель

### 8.3 Чек-лист завершения

#### Domain Layer:
- [ ] Все entities реализованы
- [ ] Все value objects реализованы
- [ ] Все domain events реализованы
- [ ] Все domain services реализованы
- [ ] Все repository interfaces определены
- [ ] 100% unit test coverage

#### Application Layer:
- [ ] Все use cases реализованы
- [ ] Все DTOs реализованы
- [ ] Все commands/queries реализованы
- [ ] Unit of Work интегрирован
- [ ] 90%+ test coverage

#### Infrastructure Layer:
- [ ] Все repositories реализованы
- [ ] Все external services интегрированы
- [ ] Все mappers реализованы
- [ ] Миграции базы данных выполнены
- [ ] 80%+ test coverage

#### Presentation Layer:
- [ ] Все handlers реализованы
- [ ] Все formatters реализованы
- [ ] Все keyboards реализованы
- [ ] Middleware настроены
- [ ] 70%+ test coverage

#### Documentation:
- [ ] Architecture documentation
- [ ] Bounded contexts documentation
- [ ] Use cases documentation
- [ ] API documentation
- [ ] Developer README

#### Deployment:
- [ ] Production environment configured
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Alerts configured
- [ ] Backup strategy implemented

---

## 📊 ИТОГОВАЯ ОЦЕНКА

### Временные затраты:
- **Фаза 0 (Подготовка):** 1-2 дня
- **Фаза 1 (Shared Kernel):** 3-4 дня
- **Фаза 2 (User Management):** 4-5 дней
- **Фаза 3 (Subscription):** 5-6 дней
- **Фаза 4 (Payment):** 6-7 дней
- **Фаза 5 (Instagram Integration):** 5-6 дней
- **Фаза 6 (Content Tracking):** 6-7 дней
- **Фаза 7 (Audience Tracking):** 5-6 дней
- **Фаза 8 (Referral):** 4-5 дней
- **Фаза 9 (Notification):** 3-4 дня
- **Фаза 10 (UoW & DI):** 3-4 дня
- **Фаза 11 (Миграция данных):** 2-3 дня
- **Фаза 12 (Интеграция):** 4-5 дней
- **Фаза 13 (Документация):** 2-3 дня

**ИТОГО:** 53-67 рабочих дней (2-3 месяца при работе 1 разработчика)

### Риски:
1. **Высокий:** Сложность миграции данных
2. **Средний:** Интеграция с внешними API
3. **Средний:** Performance regression
4. **Низкий:** Breaking changes в API

### Рекомендации:
1. Начать с Shared Kernel и User Management
2. Параллельно разрабатывать тесты
3. Использовать feature flags для постепенного rollout
4. Проводить code review на каждом этапе
5. Документировать архитектурные решения

---

**Автор плана:** AI Assistant  
**Дата создания:** 2026-03-08  
**Версия:** 1.0

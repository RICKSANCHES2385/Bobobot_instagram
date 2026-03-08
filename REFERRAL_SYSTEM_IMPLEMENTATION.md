# Referral System Implementation

**Дата**: 2026-03-08  
**Статус**: ✅ Реализовано (Domain, Application, Infrastructure, Presentation Layers)  
**Архитектура**: Clean Architecture + DDD

---

## 📋 Обзор

Реферальная программа позволяет пользователям приглашать друзей и получать 5% от их первого платежа.

### Бизнес-правила:
- Комиссия: 5% от первого платежа реферала
- Минимальная выплата: 1000₽
- Поддержка валют: RUB, XTR, USDT, TON
- Пользователь не может использовать свой собственный реферальный код
- Реферальный код можно использовать только один раз

---

## 🏗️ Архитектура

### Domain Layer ✅

#### Aggregates
- **`Referral`** (`src/domain/referral/aggregates/referral.py`)
  - Корневой агрегат реферальной системы
  - Методы:
    - `create()` - создание нового реферала
    - `apply_to_user()` - применение кода к пользователю
    - `earn_reward()` - начисление вознаграждения
    - `request_payout()` - запрос выплаты
    - `get_available_balance()` - получение доступного баланса

#### Value Objects
- **`ReferralCode`** (`src/domain/referral/value_objects/referral_code.py`)
  - 6-12 символов
  - Только буквы, цифры и подчеркивания
  - Case-insensitive (хранится в uppercase)

- **`CommissionRate`** (`src/domain/referral/value_objects/commission_rate.py`)
  - Процент комиссии (по умолчанию 5%)
  - Валидация: 0-100%
  - Метод `calculate_reward()` для расчета вознаграждения

- **`ReferralReward`** (`src/domain/referral/value_objects/referral_reward.py`)
  - Сумма вознаграждения
  - Валюта (RUB, XTR, USDT, TON)
  - Проверка минимальной суммы для выплаты

#### Events
- **`ReferralApplied`** - реферальный код применен
- **`ReferralRewardEarned`** - вознаграждение начислено
- **`ReferralPayoutRequested`** - запрос на выплату

#### Exceptions
- `InvalidReferralCodeError` - невалидный код
- `ReferralCodeAlreadyUsedError` - код уже использован
- `SelfReferralNotAllowedError` - попытка использовать свой код
- `MinimumPayoutNotReachedError` - сумма ниже минимальной
- `InvalidCommissionRateError` - невалидная комиссия
- `InvalidRewardAmountError` - невалидная сумма

#### Repository Interface
- **`ReferralRepository`** (`src/domain/referral/repositories/referral_repository.py`)
  - `save()` - сохранить реферал
  - `find_by_id()` - найти по ID
  - `find_by_referrer_user_id()` - найти по ID реферера
  - `find_by_referral_code()` - найти по коду
  - `find_by_referred_user_id()` - найти по ID реферала
  - `get_referral_stats()` - получить статистику
  - `exists_by_referral_code()` - проверить существование кода
  - `delete()` - удалить реферал

---

### Application Layer ✅

#### Use Cases
1. **`GenerateReferralCodeUseCase`** - генерация уникального кода
2. **`ApplyReferralCodeUseCase`** - применение кода при регистрации
3. **`GetReferralStatsUseCase`** - получение статистики
4. **`CalculateReferralRewardUseCase`** - расчет вознаграждения
5. **`RequestReferralPayoutUseCase`** - запрос выплаты
6. **`GetReferralLinkUseCase`** - получение реферальной ссылки

#### DTOs
- `GenerateReferralCodeDTO` - для генерации кода
- `ApplyReferralCodeDTO` - для применения кода
- `ReferralStatsDTO` - статистика рефералов
- `ReferralRewardDTO` - информация о вознаграждении
- `RequestPayoutDTO` - запрос выплаты
- `ReferralLinkDTO` - реферальная ссылка

---

### Infrastructure Layer ✅

#### Models
- **`ReferralModel`** (`src/infrastructure/persistence/models/referral_model.py`)
  - Таблица: `referrals`
  - Поля:
    - `id` - первичный ключ
    - `referrer_user_id` - ID реферера (FK to users)
    - `referral_code` - уникальный код
    - `commission_rate` - процент комиссии
    - `total_earned_amount` - всего заработано
    - `total_paid_out_amount` - всего выплачено
    - `currency` - валюта
    - `referred_user_id` - ID реферала (FK to users)
    - `applied_at` - дата применения
    - `first_payment_at` - дата первого платежа
    - `last_payout_at` - дата последней выплаты
    - `referral_count` - количество рефералов
    - `created_at`, `updated_at` - timestamps

#### Repository Implementation
- **`SqlAlchemyReferralRepository`** (`src/infrastructure/persistence/repositories/sqlalchemy_referral_repository.py`)
  - Полная реализация `ReferralRepository` interface
  - Методы конвертации: `_aggregate_to_model()`, `_model_to_aggregate()`

#### Migrations
- **`20260308_1515_create_referrals_table.py`**
  - Создание таблицы `referrals`
  - Индексы для оптимизации:
    - `ix_referrals_referrer_user_id`
    - `ix_referrals_referred_user_id`
    - `ix_referrals_referral_code`
  - Foreign keys к таблице `users`

---

### Presentation Layer ✅

#### Handlers
- **`referral_handlers.py`** (`src/presentation/telegram/handlers/referral_handlers.py`)
  - `/referral` - показать информацию о программе
  - `referral_stats` callback - статистика
  - `referral_link` callback - реферальная ссылка
  - `referral_payout` callback - запрос выплаты
  - `referral_back` callback - назад к главному меню

#### Formatters
- **`ReferralFormatter`** (`src/presentation/telegram/formatters/referral_formatter.py`)
  - `format_referral_program_info()` - информация о программе
  - `format_referral_link()` - форматирование ссылки
  - `format_referral_stats()` - форматирование статистики
  - `format_referral_applied_success()` - успешное применение
  - `format_payout_requested_success()` - успешный запрос выплаты
  - `format_minimum_payout_not_reached()` - недостаточно средств
  - `format_referral_reward_earned()` - уведомление о вознаграждении
  - `format_error()` - форматирование ошибок

---

## 📊 Статистика реализации

### Файлы
- **Domain Layer**: 11 файлов
- **Application Layer**: 8 файлов
- **Infrastructure Layer**: 3 файла
- **Presentation Layer**: 2 файла
- **Всего**: 24 файла

### Строки кода
- **Domain Layer**: ~600 строк
- **Application Layer**: ~400 строк
- **Infrastructure Layer**: ~300 строк
- **Presentation Layer**: ~400 строк
- **Всего**: ~1,700 строк

---

## 🔄 Интеграция

### Dependencies
Добавлено в `src/presentation/telegram/dependencies.py`:
- `SqlAlchemyReferralRepository` - репозиторий
- 6 use cases для работы с рефералами
- Интеграция в `UseCaseContainer`

### User Model
Обновлен `UserModel` для добавления связей:
- `referral` - реферальный код пользователя (one-to-one)
- `referred_by` - кем был приглашен (one-to-one)

---

## 🚀 Использование

### Генерация реферального кода
```python
dto = GenerateReferralCodeDTO(user_id=123, currency="RUB")
referral = await generate_referral_code_use_case.execute(dto)
```

### Применение реферального кода
```python
dto = ApplyReferralCodeDTO(
    referred_user_id=456,
    referral_code="ABC12345"
)
referral = await apply_referral_code_use_case.execute(dto)
```

### Получение статистики
```python
stats = await get_referral_stats_use_case.execute(user_id=123)
print(f"Всего рефералов: {stats.total_referrals}")
print(f"Заработано: {stats.total_earned}")
```

### Запрос выплаты
```python
referral = await request_referral_payout_use_case.execute(user_id=123)
```

---

## 📝 TODO

### Интеграция с Payment System
- [ ] Автоматическое начисление комиссии при первом платеже реферала
- [ ] Webhook для обработки успешных платежей
- [ ] Интеграция с `CompletePaymentUseCase`

### Deep Linking
- [ ] Парсинг параметра из `/start REF123`
- [ ] Автоматическое применение кода при регистрации
- [ ] Уведомление о бонусе

### Notifications
- [ ] Уведомление реферера о новом реферале
- [ ] Уведомление о заработанном вознаграждении
- [ ] Уведомление о выплате

### Tests
- [ ] Unit tests для domain layer
- [ ] Integration tests для use cases
- [ ] E2E tests для handlers

---

## ✅ Критерий завершения

Referral System считается полностью реализованным, когда:
- ✅ Domain Layer реализован
- ✅ Application Layer реализован
- ✅ Infrastructure Layer реализован
- ✅ Presentation Layer реализован
- ⏳ Интеграция с Payment System
- ⏳ Deep Linking реализован
- ⏳ Notifications настроены
- ⏳ Tests написаны

---

## 📚 Ссылки

- **DDD Rules**: `docs/solution/ruls/ddd_ruls.md`
- **Migration Plan**: `DDD_MIGRATION_REMAINING_FEATURES.md`
- **Old Implementation**: `bobobot_inst/src/models/referral.py`

---

**Статус**: 🟡 Основная функциональность реализована, требуется интеграция и тестирование

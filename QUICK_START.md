# 🚀 Быстрый старт

## Что реализовано

✅ **100% функциональность** оригинального бота  
✅ **Clean Architecture (DDD)**  
✅ **Rate Limiting** (10/мин, 100/день)  
✅ **Tracking UI** (полное меню отслеживания)  
✅ **Pagination** (Stories, Posts, Reels)  
✅ **Визуал 1:1** с оригиналом  

---

## Запуск бота

### 1. Установка зависимостей

```bash
cd bobobot_inst_ddd
uv sync
```

### 2. Настройка окружения

Создайте `.env` файл:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# HikerAPI
HIKER_API_KEY=your_hiker_api_key_here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bobobot

# Redis
REDIS_URL=redis://localhost:6379/0

# CryptoBot (опционально)
CRYPTOBOT_TOKEN=your_cryptobot_token_here

# Settings
CACHE_TTL_SECONDS=3600
RATE_LIMIT_REQUESTS_PER_MINUTE=10
RATE_LIMIT_REQUESTS_PER_DAY=100
```

### 3. Запуск БД и Redis

```bash
# PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=bobobot \
  -p 5432:5432 \
  postgres:15

# Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7
```

### 4. Миграции БД

```bash
uv run alembic upgrade head
```

### 5. Запуск бота

```bash
uv run python -m src.presentation.telegram.bot
```

---

## Основные команды

- `/start` - Начать работу с ботом
- `/instagram @username` - Получить профиль Instagram
- `/sub` - Мои отслеживания
- `/ref` - Партнёрская программа
- `/tariffs` - Тарифы подписки
- `/support` - Поддержка

---

## Архитектура

```
src/
├── domain/              # Бизнес-логика
│   ├── user_management/
│   ├── instagram_integration/
│   ├── content_tracking/
│   ├── audience_tracking/
│   ├── referral/
│   └── payment/
├── application/         # Use Cases
│   ├── user_management/
│   ├── instagram_integration/
│   ├── content_tracking/
│   └── ...
├── infrastructure/      # Внешние сервисы
│   ├── persistence/
│   ├── cache/
│   ├── external_services/
│   └── messaging/
└── presentation/        # UI (Telegram)
    └── telegram/
        ├── handlers/
        ├── formatters/
        ├── keyboards/
        └── media/
```

---

## Новые фичи (vs оригинал)

### 1. Rate Limiting ⚡
- 10 запросов/минуту
- 100 запросов/день
- Автоматические проверки во всех handlers

### 2. Tracking UI 🔔
- Полное меню отслеживания
- Выбор типа контента
- Выбор интервала (1h/6h/12h/24h)
- Динамические статусы

### 3. Pagination 📄
- Stories по 3 штуки
- Posts по 5 штук
- Reels по 3 штуки
- Кнопки "Загрузить ещё"

### 4. Улучшенный визуал 🎨
- Expandable blockquote в профиле
- Форматирование чисел (650,000,000)
- Карточки отслеживаний
- Статусные сообщения

---

## Документация

- `MIGRATION_100_PERCENT_FINAL.md` - Полный отчёт о миграции
- `FINAL_CHECKLIST.md` - Чек-лист проверки
- `RATE_LIMITING_AND_TRACKING_UI_COMPLETE.md` - Детали Rate Limiting и Tracking UI
- `FINAL_MIGRATION_PLAN.md` - Исходный план миграции

---

## Тестирование

### Проверка Rate Limiting

```python
# Сделайте 11 запросов за минуту
for i in range(11):
    await bot.send_message(chat_id, "/instagram cristiano")
    
# Должно появиться сообщение:
# ⏱ Превышен лимит запросов в минуту (11/10)
```

### Проверка Tracking UI

1. Отправьте `/instagram cristiano`
2. Нажмите "📊 Отслеживать"
3. Выберите "📖 Истории"
4. Выберите "⏰ Каждый час"
5. Проверьте статус: "✅ каждый час"

### Проверка Pagination

1. Отправьте `/instagram cristiano`
2. Нажмите "👀 Посмотреть истории"
3. Получите первые 3 истории
4. Нажмите "📖 Загрузить ещё (N)"
5. Получите следующие 3 истории

---

## Troubleshooting

### Бот не запускается

```bash
# Проверьте .env файл
cat .env

# Проверьте подключение к БД
psql -h localhost -U user -d bobobot

# Проверьте подключение к Redis
redis-cli ping
```

### Ошибки миграций

```bash
# Откатить миграции
uv run alembic downgrade -1

# Применить заново
uv run alembic upgrade head
```

### Rate Limiting не работает

```bash
# Проверьте Redis
redis-cli
> KEYS rate_limit:*
> GET rate_limit:user:123:minute:20260308131
```

---

## 🎉 Готово!

Бот полностью готов к работе. Все фичи реализованы, визуал соответствует оригиналу 1:1.

**Приятного использования!** 🚀

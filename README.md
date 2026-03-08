# 🤖 BOBOBOT_INST_DDD

> Instagram Data Bot на чистой DDD архитектуре

## 📋 О проекте

Telegram бот для получения данных из Instagram с использованием Domain-Driven Design (DDD) архитектуры.

**Версия:** 2.0 - Complete Coverage  
**Покрытие функционала:** 100% (46 Use Cases)  
**Статус:** 🚀 В разработке

## 🏗️ Архитектура

Проект построен на принципах:
- **Clean Architecture** (Hexagonal Architecture)
- **Domain-Driven Design** (DDD)
- **SOLID принципы**
- **Event-Driven Architecture**

### Слои:

```
┌─────────────────────────────────────┐
│     PRESENTATION LAYER              │
│  (Telegram Handlers, CLI)           │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     APPLICATION LAYER               │
│  (Use Cases, DTOs, Commands)        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     DOMAIN LAYER                    │
│  (Entities, Value Objects, Events)  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     INFRASTRUCTURE LAYER            │
│  (Repositories, External Services)  │
└─────────────────────────────────────┘
```

### Bounded Contexts (8):

1. **User Management** - управление пользователями
2. **Subscription** - управление подписками
3. **Payment** - обработка платежей (Stars, Robokassa, CryptoBot)
4. **Instagram Integration** - интеграция с Instagram API
5. **Content Tracking** - отслеживание контента
6. **Audience Tracking** - отслеживание аудитории (платное)
7. **Referral** - реферальная система
8. **Notification** - система уведомлений

## 🚀 Быстрый старт

### Требования:

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (опционально)

### Установка:

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd bobobot_inst_ddd
```

2. Создать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows
```

3. Установить зависимости:
```bash
pip install -e ".[dev]"
```

4. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактировать .env файл
```

5. Запустить инфраструктуру:
```bash
docker-compose up -d
```

6. Применить миграции:
```bash
alembic upgrade head
```

7. Запустить тесты:
```bash
pytest
```

## 📁 Структура проекта

```
bobobot_inst_ddd/
├── src/
│   ├── domain/              # Domain Layer
│   │   ├── shared/          # Shared Kernel
│   │   ├── user_management/
│   │   ├── subscription/
│   │   ├── payment/
│   │   ├── instagram_integration/
│   │   ├── content_tracking/
│   │   ├── audience_tracking/
│   │   ├── referral/
│   │   └── notification/
│   ├── application/         # Application Layer
│   │   ├── shared/
│   │   └── [contexts]/
│   ├── infrastructure/      # Infrastructure Layer
│   │   ├── persistence/
│   │   ├── cache/
│   │   ├── external_services/
│   │   ├── messaging/
│   │   └── config/
│   └── presentation/        # Presentation Layer
│       ├── telegram/
│       └── cli/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                    # Документация
├── alembic/                 # Миграции БД
└── scripts/                 # Утилиты
```

## 🧪 Тестирование

### Запуск всех тестов:
```bash
pytest
```

### Запуск с покрытием:
```bash
pytest --cov=src --cov-report=html
```

### Запуск конкретных тестов:
```bash
# Unit тесты
pytest tests/unit/ -v

# Integration тесты
pytest tests/integration/ -v

# E2E тесты
pytest tests/e2e/ -v
```

## 📚 Документация

- [README_V2.md](README_V2.md) - Полный обзор V2.0
- [QUICK_START_V2.md](QUICK_START_V2.md) - Пошаговая инструкция
- [PROGRESS_CHECKLIST.md](PROGRESS_CHECKLIST.md) - Чеклист прогресса
- [docs/solution/v2_updates/00_V2_SUMMARY.md](docs/solution/v2_updates/00_V2_SUMMARY.md) - Итоговая сводка V2.0
- [docs/solution/EXAMPLES_VALUE_OBJECTS.md](docs/solution/EXAMPLES_VALUE_OBJECTS.md) - Примеры Value Objects
- [docs/solution/EXAMPLES_ENTITIES_AGGREGATES.md](docs/solution/EXAMPLES_ENTITIES_AGGREGATES.md) - Примеры Entities

## 🛠️ Разработка

### Линтинг и форматирование:
```bash
# Black
black src tests

# Ruff
ruff check src tests

# MyPy
mypy src
```

### Создание миграции:
```bash
alembic revision --autogenerate -m "Description"
```

### Применение миграций:
```bash
alembic upgrade head
```

## 📊 Прогресс разработки

Текущий прогресс: **5%**

- [x] Этап 0: Подготовка (70%)
- [ ] Этап 1: Shared Kernel (0%)
- [ ] Этап 2-9: Bounded Contexts (0%)
- [ ] Этап 10-13: Финализация (0%)

Подробный чеклист: [PROGRESS_CHECKLIST.md](PROGRESS_CHECKLIST.md)

## 🤝 Вклад в проект

1. Fork проекта
2. Создать feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменений (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Открыть Pull Request

## 📝 Лицензия

[MIT License](LICENSE)

## 📞 Контакты

**Проект:** bobobot_inst_ddd  
**Версия:** 2.0 - Complete Coverage  
**Дата:** 2026-03-08

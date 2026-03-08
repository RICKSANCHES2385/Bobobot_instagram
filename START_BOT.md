# Как запустить бота

## ✅ Миграции применены успешно!

## 🚀 Команда для запуска

```bash
cd bobobot_inst_ddd
uv run python -m run_bot
```

## ⚠️ Текущая проблема

Есть ошибка с `TrackingChecker` - это background task для проверки обновлений контента.

**Решение**: Временно отключить background tasks в `dependencies.py` или исправить инициализацию.

## 📝 Что исправлено

1. ✅ Миграции - исправлены типы foreign keys
2. ✅ Импорты - исправлены все неправильные импорты:
   - `DomainEvent` из `src.domain.shared.events`
   - `DomainException` из `src.domain.shared.exceptions`
   - `Currency` из `src.domain.shared.value_objects.money`
   - `AggregateRoot` из `src.domain.shared.entities.base`
   - `Base` из `src.infrastructure.persistence.base`
   - `get_logger` из `src.infrastructure.logging.logger`
3. ✅ Dataclass - исправлены порядки аргументов
4. ✅ .env - добавлен `TELEGRAM_BOT_TOKEN`
5. ✅ Database - изменен на `postgresql+asyncpg`
6. ✅ asyncpg - установлен пакет

## 🔧 Осталось исправить

1. ⚠️ `TrackingChecker` - неправильная инициализация
2. ⚠️ Background tasks - возможно нужно отключить временно

## 💡 Быстрое решение

Откройте `src/presentation/telegram/dependencies.py` и закомментируйте строки с `TrackingChecker` (примерно строка 150-160).

Или исправьте инициализацию `TrackingChecker` чтобы принимать правильные аргументы.

---

**Статус**: Почти готово! Осталась одна мелкая проблема с background tasks.

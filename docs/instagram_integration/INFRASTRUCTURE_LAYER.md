# Instagram Integration - Infrastructure Layer

## Overview

Infrastructure Layer реализует адаптеры для внешних сервисов и технические детали интеграции с Instagram API через HikerAPI.

## Components

### HikerAPIAdapter

Адаптер для интеграции с HikerAPI - внешним сервисом для доступа к Instagram данным.

**Location:** `src/infrastructure/external_services/hiker_api/hiker_api_adapter.py`

**Features:**
- Асинхронные HTTP запросы с retry логикой (tenacity)
- Автоматический маппинг API responses в Domain Entities
- Поддержка пагинации для больших наборов данных
- Обработка различных форматов ответов API

**Methods:**
- `fetch_profile_by_username(username)` - получить профиль по username
- `fetch_profile_by_id(user_id)` - получить профиль по ID
- `fetch_stories(user_id)` - получить stories пользователя
- `fetch_posts(user_id, cursor)` - получить посты с пагинацией
- `fetch_reels(user_id, cursor)` - получить reels с пагинацией
- `fetch_highlights(user_id)` - получить highlights
- `fetch_highlight_stories(highlight_id)` - получить stories из highlight
- `fetch_followers(user_id, cursor)` - получить подписчиков с пагинацией
- `fetch_following(user_id, cursor)` - получить подписки с пагинацией
- `fetch_comments(media_id, cursor)` - получить комментарии с пагинацией
- `fetch_tagged_posts(user_id, cursor)` - получить tagged posts с пагинацией
- `search_users(query)` - поиск пользователей

### Configuration

**Location:** `src/infrastructure/config/instagram_config.py`

```python
class InstagramConfig(BaseSettings):
    hikerapi_key: str  # HikerAPI access key
    hikerapi_base_url: str = "https://api.hikerapi.com"
    cache_ttl_seconds: int = 300
    rate_limit_requests_per_minute: int = 10
```

## Usage Example

```python
from src.infrastructure.external_services.hiker_api import HikerAPIAdapter
from src.infrastructure.config.instagram_config import instagram_config

# Initialize adapter
adapter = HikerAPIAdapter(
    api_key=instagram_config.hikerapi_key,
    base_url=instagram_config.hikerapi_base_url
)

# Fetch profile
from src.domain.instagram_integration.value_objects.instagram_username import InstagramUsername
username = InstagramUsername("example_user")
profile = await adapter.fetch_profile_by_username(username)

# Fetch posts with pagination
from src.domain.instagram_integration.value_objects.instagram_user_id import InstagramUserId
user_id = InstagramUserId("123456")
posts, next_cursor = await adapter.fetch_posts(user_id)

# Close adapter
await adapter.close()
```

## Data Mapping

Адаптер автоматически преобразует API responses в Domain Entities:

- **API Response** → **InstagramProfile** (с Bio, ProfileStatistics)
- **API Response** → **Story** (с MediaId, MediaUrl)
- **API Response** → **Post** (с MediaId, Caption, media_urls list)
- **API Response** → **Reel** (с MediaId, Caption, video_url)
- **API Response** → **Highlight** (с HighlightId, HighlightTitle)
- **API Response** → **Comment** (с CommentId, CommentText)
- **API Response** → **UserSearchResult**

## Error Handling

- **Retry Logic:** 3 попытки с exponential backoff (2-10 секунд)
- **HTTP Errors:** Автоматическая обработка через `httpx.HTTPStatusError`
- **Network Errors:** Обработка через `httpx.RequestError`

## Testing

**Unit Tests:** `tests/unit/infrastructure/external_services/test_hiker_api_adapter.py`

- 11 тестов
- 100% покрытие публичных методов
- Моки для HTTP клиента

**Integration Tests:** `tests/integration/instagram_integration/test_instagram_use_cases_integration.py`

- Тесты Use Cases с адаптером
- Проверка корректности маппинга данных

## Dependencies

- `httpx` - асинхронный HTTP клиент
- `tenacity` - retry логика
- `pydantic` - конфигурация и валидация

## Performance Considerations

- Асинхронные операции для высокой производительности
- Retry логика для надежности
- Поддержка пагинации для больших наборов данных
- Рекомендуется использовать connection pooling

## Future Enhancements

- [ ] Cache layer (Redis) для уменьшения API calls
- [ ] Rate limiter для соблюдения API limits
- [ ] Metrics и monitoring
- [ ] Circuit breaker pattern для fault tolerance

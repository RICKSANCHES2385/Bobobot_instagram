# 🏗️ ОБНОВЛЕННАЯ СТРУКТУРА ПРОЕКТА V2.0

## 📋 ПОЛНАЯ СТРУКТУРА С 100% ПОКРЫТИЕМ

```
bobobot_inst_ddd/
├── src/
│   ├── domain/                                     # DOMAIN LAYER
│   │   ├── __init__.py
│   │   ├── shared/                                 # Shared Kernel
│   │   │   ├── __init__.py
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── identifier.py
│   │   │   │   ├── money.py
│   │   │   │   └── date_range.py
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   └── base.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   └── event_dispatcher.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   └── validation.py
│   │   │   └── specifications/
│   │   │       ├── __init__.py
│   │   │       └── base.py
│   │   │
│   │   ├── instagram_integration/                  # Instagram Integration BC
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
│   │   │   │   ├── profile_picture.py
│   │   │   │   ├── request_type.py
│   │   │   │   ├── content_type.py                 # 🔄 UPDATED
│   │   │   │   ├── highlight_id.py                 # 🆕 NEW
│   │   │   │   ├── highlight_title.py              # 🆕 NEW
│   │   │   │   ├── highlight_cover_url.py          # 🆕 NEW
│   │   │   │   ├── comment_id.py                   # 🆕 NEW
│   │   │   │   ├── comment_text.py                 # 🆕 NEW
│   │   │   │   ├── comment_author.py               # 🆕 NEW
│   │   │   │   ├── followers_list.py               # 🆕 NEW
│   │   │   │   └── following_list.py               # 🆕 NEW
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── profile_data_fetched.py
│   │   │   │   ├── profile_not_found.py
│   │   │   │   ├── profile_is_private.py
│   │   │   │   ├── rate_limit_exceeded.py
│   │   │   │   ├── highlights_data_fetched.py      # 🆕 NEW
│   │   │   │   ├── highlight_stories_data_fetched.py # 🆕 NEW
│   │   │   │   ├── followers_data_fetched.py       # 🆕 NEW
│   │   │   │   ├── following_data_fetched.py       # 🆕 NEW
│   │   │   │   ├── comments_data_fetched.py        # 🆕 NEW
│   │   │   │   └── tagged_posts_data_fetched.py    # 🆕 NEW
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rate_limiting_service.py
│   │   │   │   └── cache_service.py
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── profile_not_found.py
│   │   │   │   ├── private_profile.py
│   │   │   │   ├── rate_limit_exceeded.py
│   │   │   │   └── highlight_not_found.py          # 🆕 NEW
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── instagram_request_repository.py
│   │   │
│   │   ├── [other bounded contexts...]
│   │
│   ├── application/                                # APPLICATION LAYER
│   │   ├── __init__.py
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── unit_of_work.py
│   │   │   ├── command.py
│   │   │   ├── query.py
│   │   │   ├── dto.py
│   │   │   └── result.py
│   │   │
│   │   ├── instagram_integration/
│   │   │   ├── __init__.py
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── fetch_instagram_profile.py
│   │   │   │   ├── fetch_instagram_highlights.py   # 🆕 NEW
│   │   │   │   ├── fetch_instagram_highlight_stories.py # 🆕 NEW
│   │   │   │   ├── fetch_instagram_followers.py    # 🆕 NEW
│   │   │   │   ├── fetch_instagram_following.py    # 🆕 NEW
│   │   │   │   ├── fetch_instagram_comments.py     # 🆕 NEW
│   │   │   │   └── fetch_instagram_tagged_posts.py # 🆕 NEW
│   │   │   ├── queries/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── get_instagram_profile.py
│   │   │   │   ├── get_instagram_stories.py
│   │   │   │   ├── get_instagram_posts.py
│   │   │   │   └── search_instagram_users.py
│   │   │   ├── dtos/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── instagram_profile_dto.py
│   │   │   │   ├── instagram_content_dto.py
│   │   │   │   ├── highlight_dto.py                # 🆕 NEW
│   │   │   │   ├── highlights_list_dto.py          # 🆕 NEW
│   │   │   │   ├── highlight_story_dto.py          # 🆕 NEW
│   │   │   │   ├── highlight_stories_list_dto.py   # 🆕 NEW
│   │   │   │   ├── follower_dto.py                 # 🆕 NEW
│   │   │   │   ├── followers_list_dto.py           # 🆕 NEW
│   │   │   │   ├── following_dto.py                # 🆕 NEW
│   │   │   │   ├── following_list_dto.py           # 🆕 NEW
│   │   │   │   ├── comment_dto.py                  # 🆕 NEW
│   │   │   │   ├── comments_list_dto.py            # 🆕 NEW
│   │   │   │   ├── tagged_post_dto.py              # 🆕 NEW
│   │   │   │   └── tagged_posts_list_dto.py        # 🆕 NEW
│   │   │   └── use_cases/
│   │   │       ├── __init__.py
│   │   │       ├── fetch_instagram_profile_use_case.py
│   │   │       ├── fetch_instagram_stories_use_case.py
│   │   │       ├── fetch_instagram_posts_use_case.py
│   │   │       ├── fetch_instagram_reels_use_case.py
│   │   │       ├── search_instagram_users_use_case.py
│   │   │       ├── fetch_instagram_highlights_use_case.py        # 🆕 NEW
│   │   │       ├── fetch_instagram_highlight_stories_use_case.py # 🆕 NEW
│   │   │       ├── fetch_instagram_followers_use_case.py         # 🆕 NEW
│   │   │       ├── fetch_instagram_following_use_case.py         # 🆕 NEW
│   │   │       ├── fetch_instagram_comments_use_case.py          # 🆕 NEW
│   │   │       └── fetch_instagram_tagged_posts_use_case.py      # 🆕 NEW
│   │   │
│   │   ├── [other bounded contexts...]
│   │
│   ├── infrastructure/                             # INFRASTRUCTURE LAYER
│   │   ├── __init__.py
│   │   ├── persistence/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── unit_of_work.py
│   │   │   ├── sqlalchemy/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user_model.py
│   │   │   │   │   ├── subscription_model.py
│   │   │   │   │   ├── payment_model.py
│   │   │   │   │   ├── instagram_tracking_model.py
│   │   │   │   │   ├── audience_tracking_model.py
│   │   │   │   │   ├── referral_model.py
│   │   │   │   │   └── notification_model.py
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── user_repository.py
│   │   │   │   │   ├── subscription_repository.py
│   │   │   │   │   ├── payment_repository.py
│   │   │   │   │   ├── instagram_request_repository.py
│   │   │   │   │   ├── content_tracking_repository.py
│   │   │   │   │   ├── audience_tracking_repository.py
│   │   │   │   │   ├── referral_repository.py
│   │   │   │   │   └── notification_repository.py
│   │   │   │   └── mappers/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── user_mapper.py
│   │   │   │       ├── subscription_mapper.py
│   │   │   │       ├── payment_mapper.py
│   │   │   │       ├── tracking_mapper.py
│   │   │   │       ├── referral_mapper.py
│   │   │   │       └── notification_mapper.py
│   │   │   └── migrations/
│   │   │       └── versions/
│   │   │
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── redis_cache.py
│   │   │   └── in_memory_cache.py
│   │   │
│   │   ├── external_services/
│   │   │   ├── __init__.py
│   │   │   ├── instagram/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── hikerapi_client.py
│   │   │   │   └── instagram_api_adapter.py
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
│   │   │   ├── event_bus.py
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
│   │       ├── settings.py
│   │       └── dependency_injection.py
│   │
│   └── presentation/                               # PRESENTATION LAYER
│       ├── __init__.py
│       ├── telegram/
│       │   ├── __init__.py
│       │   ├── bot.py
│       │   ├── handlers/
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
│       └── cli/
│           ├── __init__.py
│           └── commands.py
│
├── tests/                                          # TESTS
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── shared/
│   │   │   │   ├── test_base_value_object.py
│   │   │   │   ├── test_base_entity.py
│   │   │   │   ├── test_aggregate_root.py
│   │   │   │   └── test_domain_event.py
│   │   │   ├── instagram_integration/
│   │   │   │   ├── test_instagram_username.py
│   │   │   │   ├── test_instagram_user_id.py
│   │   │   │   ├── test_profile_statistics.py
│   │   │   │   ├── test_highlight_id.py           # 🆕 NEW
│   │   │   │   ├── test_comment_id.py             # 🆕 NEW
│   │   │   │   └── test_followers_list.py         # 🆕 NEW
│   │   │   └── [other contexts...]
│   │   └── application/
│   │       ├── __init__.py
│   │       ├── instagram_integration/
│   │       │   ├── test_fetch_instagram_profile_use_case.py
│   │       │   ├── test_fetch_instagram_highlights_use_case.py        # 🆕 NEW
│   │       │   ├── test_fetch_instagram_highlight_stories_use_case.py # 🆕 NEW
│   │       │   ├── test_fetch_instagram_followers_use_case.py         # 🆕 NEW
│   │       │   ├── test_fetch_instagram_following_use_case.py         # 🆕 NEW
│   │       │   ├── test_fetch_instagram_comments_use_case.py          # 🆕 NEW
│   │       │   └── test_fetch_instagram_tagged_posts_use_case.py      # 🆕 NEW
│   │       └── [other contexts...]
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── repositories/
│   │   ├── external_services/
│   │   └── use_cases/
│   │
│   ├── e2e/
│   │   ├── __init__.py
│   │   └── telegram_bot/
│   │
│   └── fixtures/
│       ├── __init__.py
│       ├── domain_fixtures.py
│       └── infrastructure_fixtures.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── docs/
│   ├── architecture/
│   │   ├── bounded_contexts.md
│   │   ├── domain_model.md
│   │   └── infrastructure.md
│   ├── use_cases/
│   └── api/
│
├── scripts/
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
└── REFACTORING_MASTER_PLAN_V2_COMPLETE.md
```

---

## 📊 СТАТИСТИКА ИЗМЕНЕНИЙ V2.0

### Новые файлы:

#### Domain Layer:
- Value Objects: +8 файлов
- Events: +6 файлов
- Exceptions: +1 файл

#### Application Layer:
- Commands: +6 файлов
- DTOs: +12 файлов
- Use Cases: +6 файлов

#### Tests:
- Unit tests (domain): +9 файлов
- Unit tests (application): +6 файлов

**Итого новых файлов:** +54

### Обновленные файлы:
- content_type.py (enum расширен)
- request_type.py (enum расширен)

**Итого обновленных файлов:** +2

---

## 🎯 ПОЛНОЕ ПОКРЫТИЕ ФУНКЦИОНАЛА

### Instagram Integration Context:

| Функция | Use Case | Статус |
|---------|----------|--------|
| Получение профиля | FetchInstagramProfileUseCase | ✅ |
| Posts | FetchInstagramPostsUseCase | ✅ |
| Reels | FetchInstagramReelsUseCase | ✅ |
| Stories | FetchInstagramStoriesUseCase | ✅ |
| Highlights (список) | FetchInstagramHighlightsUseCase | ✅ 🆕 |
| Highlight Stories | FetchInstagramHighlightStoriesUseCase | ✅ 🆕 |
| Followers | FetchInstagramFollowersUseCase | ✅ 🆕 |
| Following | FetchInstagramFollowingUseCase | ✅ 🆕 |
| Comments | FetchInstagramCommentsUseCase | ✅ 🆕 |
| Tagged Posts | FetchInstagramTaggedPostsUseCase | ✅ 🆕 |
| Поиск | SearchInstagramUsersUseCase | ✅ |

**Покрытие:** 11/11 (100%) ✅

---

**Дата создания:** 2026-03-08  
**Автор:** Kiro AI Assistant  
**Версия:** 2.0  
**Статус:** Готово ✅

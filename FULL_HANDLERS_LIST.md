# Полный список handlers для реализации

## Command Handlers (commands.py)
- [x] `/start` - Регистрация, trial, главное меню
- [x] `/tariffs` - Показать тарифы
- [x] `/sub` - Мои отслеживания
- [x] `/ref` - Партнёрская программа
- [x] `/support` - Поддержка
- [x] `/force` - Принудительная проверка обновлений
- [ ] `/instagram @username` - Получить профиль Instagram
- [ ] `/buy` - Купить подписку

## Instagram Handlers (instagram_handlers.py)
### Profile
- [ ] `instagram_command` - /instagram @username
- [ ] `handle_text_message` - Обработка username/link в тексте
- [ ] `send_user_profile` - Отправка профиля с фото
- [ ] `show_profile_from_callback` - Показать профиль из callback
- [ ] `handle_profile_callback` - ig_profile_{user_id}_{username}
- [ ] `handle_back_to_profile` - ig_back_{user_id}_{username}

### Content
- [ ] `handle_stories` - Загрузка stories (батчами по 3)
- [ ] `handle_stories_next` - Следующая порция stories
- [ ] `handle_posts` - Загрузка posts (батчами по 5)
- [ ] `handle_posts_next` - Следующая порция posts
- [ ] `handle_reels` - Загрузка reels (батчами по 3)
- [ ] `handle_reels_next` - Следующая порция reels
- [ ] `handle_highlights` - Список highlights
- [ ] `handle_highlight_view` - Просмотр highlight
- [ ] `handle_highlight_stories` - Stories из highlight
- [ ] `handle_highlight_next` - Следующая порция highlight stories
- [ ] `handle_tagged` - Tagged posts
- [ ] `handle_tagged_posts` - Загрузка tagged posts
- [ ] `handle_tagged_next` - Следующая порция tagged

### Social
- [ ] `handle_followers` - Первые 50 подписчиков
- [ ] `handle_followers_download` - Скачать всех подписчиков (txt)
- [ ] `handle_following` - Первые 50 подписок
- [ ] `handle_following_download` - Скачать все подписки (txt)
- [ ] `handle_comments` - Комментарии к посту

### Downloads
- [ ] `handle_posts_download` - Скачать список всех постов (txt)
- [ ] `handle_reels_download` - Скачать список всех reels (txt)

### Media Sending
- [ ] `send_media_post` - Отправка одного media (фото/видео/альбом)

## Tracking Handlers (tracking_handlers.py)
### Menu
- [ ] `show_tracking_menu` - Меню настройки отслеживания
- [ ] `get_tracking_menu_keyboard` - Клавиатура меню
- [ ] `get_tracking_interval_keyboard` - Клавиатура интервалов

### Actions
- [ ] `handle_tracking_type_selection` - Выбор типа (stories/posts/followers/following)
- [ ] `handle_tracking_interval_set` - Установка интервала (1h/6h/12h/24h)
- [ ] `handle_tracking_disable_single` - Отключить один тип
- [ ] `handle_tracking_menu_back` - Назад в меню
- [ ] `handle_track_request` - ig_track_{user_id}_{username}

### Audience Tracking (платная функция)
- [ ] `handle_audience_payment` - Оплата audience tracking
- [ ] `handle_audience_precheckout` - Pre-checkout для audience
- [ ] `handle_audience_successful_payment` - Успешная оплата audience

## Payment Handlers (payment_handlers.py)
### Main
- [ ] `buy_subscription_command` - /buy - выбор способа оплаты
- [ ] `payment_menu_callback` - Назад к выбору способа
- [ ] `cleanup_expired_payments_task` - Фоновая задача очистки

### Telegram Stars
- [ ] `payment_stars_callback` - Показать планы Stars
- [ ] `handle_buy_callback` - buy_{plan_code} - создание invoice
- [ ] `precheckout_callback` - Pre-checkout query
- [ ] `successful_payment_callback` - Успешная оплата

### Robokassa
- [ ] `payment_robokassa_callback` - Показать планы Robokassa
- [ ] `robokassa_buy_callback` - robokassa_buy_{plan_code}
- [ ] `robokassa_result_callback` - Webhook результата
- [ ] `robokassa_success_callback` - Успешная оплата
- [ ] `robokassa_fail_callback` - Неудачная оплата

## Crypto Bot Handlers (crypto_bot_handlers.py)
### Main
- [ ] `crypto_bot_callback` - Выбор криптовалюты
- [ ] `crypto_bot_ton_callback` - Планы TON
- [ ] `crypto_bot_usdt_callback` - Планы USDT

### Purchase
- [ ] `crypto_bot_ton_buy_callback` - Покупка за TON
- [ ] `crypto_bot_usdt_buy_callback` - Покупка за USDT
- [ ] `crypto_bot_check_payment` - Проверка статуса оплаты

## Keyboards
### Main Menu (main_menu.py)
- [x] `get_start_keyboard` - Главное меню

### Instagram Menu (instagram_menu.py)
- [x] `get_profile_keyboard` - Действия с профилем
- [x] `get_back_to_profile_keyboard` - Назад к профилю

### Tracking Menu (tracking_menu.py)
- [ ] `get_tracking_menu_keyboard` - Меню отслеживания
- [ ] `get_tracking_interval_keyboard` - Выбор интервала

### Payment Menu (payment_menu.py)
- [ ] `get_payment_method_keyboard` - Выбор способа оплаты
- [ ] `get_stars_plans_keyboard` - Планы Stars
- [ ] `get_robokassa_plans_keyboard` - Планы Robokassa
- [ ] `get_crypto_plans_keyboard` - Планы Crypto

## Formatters
### Profile Formatter (profile_formatter.py)
- [ ] `format_profile_text` - Форматирование профиля
- [ ] `format_tracking_status` - Форматирование статуса отслеживания
- [ ] `format_audience_status` - Форматирование audience tracking

### Content Formatter (content_formatter.py)
- [ ] `format_story_caption` - Подпись к story
- [ ] `format_post_caption` - Подпись к посту
- [ ] `format_reel_caption` - Подпись к reel
- [ ] `format_highlight_caption` - Подпись к highlight

### List Formatter (list_formatter.py)
- [ ] `format_followers_list` - Список подписчиков
- [ ] `format_following_list` - Список подписок
- [ ] `format_posts_list` - Список постов (для txt)
- [ ] `format_reels_list` - Список reels (для txt)

## Middleware
### Subscription Check (subscription_check.py)
- [ ] `SubscriptionCheckMiddleware` - Проверка подписки

### Rate Limit (rate_limit.py)
- [ ] `RateLimitMiddleware` - Rate limiting

## Utilities
### Media Downloader (media_downloader.py)
- [ ] `download_media` - Скачивание медиа
- [ ] `download_album` - Скачивание альбома
- [ ] `send_media_group` - Отправка группы медиа

---

**Итого:** ~80+ функций для полной реализации

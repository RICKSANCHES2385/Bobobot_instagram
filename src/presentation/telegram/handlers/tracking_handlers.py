"""Tracking handlers for Telegram bot."""

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container

logger = get_logger(__name__)


def get_tracking_menu_keyboard(user_id: str, username: str) -> InlineKeyboardMarkup:
    """Get tracking configuration menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Stories", callback_data=f"track_type_stories_{user_id}_{username}")],
        [InlineKeyboardButton(text="📸 Posts", callback_data=f"track_type_posts_{user_id}_{username}")],
        [InlineKeyboardButton(text="👥 Followers", callback_data=f"track_type_followers_{user_id}_{username}")],
        [InlineKeyboardButton(text="👤 Following", callback_data=f"track_type_following_{user_id}_{username}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_back_{user_id}_{username}")]
    ])


def get_tracking_interval_keyboard(tracking_type: str, user_id: str, username: str) -> InlineKeyboardMarkup:
    """Get tracking interval selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱ 1 час", callback_data=f"track_interval_{tracking_type}_1h_{user_id}_{username}")],
        [InlineKeyboardButton(text="⏱ 6 часов", callback_data=f"track_interval_{tracking_type}_6h_{user_id}_{username}")],
        [InlineKeyboardButton(text="⏱ 12 часов", callback_data=f"track_interval_{tracking_type}_12h_{user_id}_{username}")],
        [InlineKeyboardButton(text="⏱ 24 часа", callback_data=f"track_interval_{tracking_type}_24h_{user_id}_{username}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_track_{user_id}_{username}")]
    ])


async def show_tracking_menu(callback: CallbackQuery, user_id: str, username: str) -> None:
    """Show tracking configuration menu."""
    # TODO: Get current tracking status via GetUserTrackingsUseCase
    
    text = (
        f"📊 <b>Отслеживание @{username}</b>\n\n"
        "Выберите что отслеживать:\n\n"
        "📖 Stories - новые истории\n"
        "📸 Posts - новые публикации\n"
        "👥 Followers - изменения подписчиков\n"
        "👤 Following - изменения подписок\n\n"
        "🔔 Вы будете получать уведомления о новом контенте"
    )
    
    keyboard = get_tracking_menu_keyboard(user_id, username)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def tracking_start_callback(callback: CallbackQuery) -> None:
    """Handle start tracking callback - show menu."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: ig_track_{user_id}_{username}
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Opening tracking menu for {username} (user_id={user_id})")

    await show_tracking_menu(callback, user_id, username)


async def handle_tracking_type_selection(callback: CallbackQuery) -> None:
    """Handle tracking type selection - show interval menu."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: track_type_{type}_{user_id}_{username}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    tracking_type = parts[2]
    user_id = parts[3]
    username = parts[4]

    logger.info(f"Selected tracking type {tracking_type} for {username}")

    type_names = {
        "stories": "Stories",
        "posts": "Posts",
        "followers": "Followers",
        "following": "Following"
    }

    text = (
        f"📊 <b>Отслеживание {type_names.get(tracking_type, tracking_type)}</b>\n"
        f"Профиль: @{username}\n\n"
        "Выберите интервал проверки:"
    )

    keyboard = get_tracking_interval_keyboard(tracking_type, user_id, username)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def handle_tracking_interval_set(callback: CallbackQuery) -> None:
    """Handle tracking interval selection - create tracking."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    # Parse: track_interval_{type}_{interval}_{user_id}_{username}
    parts = callback.data.split("_", 5)
    if len(parts) < 6:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    tracking_type = parts[2]
    interval = parts[3]
    user_id = int(parts[4])
    username = parts[5]

    logger.info(f"Creating tracking {tracking_type} for {username} with interval {interval}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Check subscription status
        sub_status = await use_cases.check_subscription_status.execute(user_id)
        if not sub_status.is_active:
            await callback.message.answer(
                "❌ Для отслеживания нужна активная подписка\n\n"
                "Используйте /buy для покупки подписки"
            )
            return
        
        # Map interval to hours
        interval_hours = {
            "1h": 1,
            "6h": 6,
            "12h": 12,
            "24h": 24
        }
        
        # Map tracking type to content type
        from src.domain.content_tracking.value_objects.content_type import ContentType, ContentTypeEnum
        content_type_map = {
            "stories": ContentType(ContentTypeEnum.STORIES),
            "posts": ContentType(ContentTypeEnum.POSTS),
            "followers": ContentType(ContentTypeEnum.STORIES),  # Fallback to STORIES for now
            "following": ContentType(ContentTypeEnum.STORIES)   # Fallback to STORIES for now
        }
        
        # Start tracking
        await use_cases.start_tracking.execute(
            user_id=user_id,
            instagram_username=username,
            content_types=[content_type_map[tracking_type]],
            check_interval_hours=interval_hours[interval]
        )
        
        type_names = {
            "stories": "Stories",
            "posts": "Posts",
            "followers": "Followers",
            "following": "Following"
        }

        interval_names = {
            "1h": "1 час",
            "6h": "6 часов",
            "12h": "12 часов",
            "24h": "24 часа"
        }
        
        text = (
            f"✅ <b>Отслеживание активировано</b>\n\n"
            f"Профиль: @{username}\n"
            f"Тип: {type_names.get(tracking_type, tracking_type)}\n"
            f"Интервал: {interval_names.get(interval, interval)}\n\n"
            "🔔 Вы будете получать уведомления о новом контенте"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад к профилю", callback_data=f"ig_back_{user_id}_{username}")]
        ])
        
        await callback.message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error creating tracking for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось создать отслеживание\n\n"
            f"Ошибка: {str(e)}"
        )


async def handle_tracking_disable_single(callback: CallbackQuery) -> None:
    """Handle disabling single tracking type."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: track_disable_{type}_{user_id}_{username}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    tracking_type = parts[2]
    user_id = parts[3]
    username = parts[4]

    logger.info(f"Disabling tracking {tracking_type} for {username}")

    # TODO: Call StopTrackingUseCase for specific type
    
    await callback.answer(f"✅ Отслеживание {tracking_type} отключено", show_alert=True)
    await show_tracking_menu(callback, user_id, username)


async def handle_tracking_menu_back(callback: CallbackQuery) -> None:
    """Handle back to tracking menu."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: track_menu_{user_id}_{username}
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    await show_tracking_menu(callback, user_id, username)


async def tracking_stop_callback(callback: CallbackQuery) -> None:
    """Handle stop all tracking callback."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    # Parse: unsubscribe_tracking_{username}
    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    username = parts[2]
    user_id = callback.from_user.id

    logger.info(f"Stopping all tracking for {username}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Get user trackings
        trackings = await use_cases.get_user_trackings.execute(user_id)
        
        # Find tracking for this username
        tracking = next((t for t in trackings if t.instagram_username == username), None)
        
        if tracking:
            # Stop tracking
            await use_cases.stop_tracking.execute(tracking.id)
            
            await callback.message.edit_text(
                f"✅ Вы отписались от отслеживания <b>@{username}</b>"
            )
        else:
            await callback.message.edit_text(
                f"❌ Отслеживание @{username} не найдено"
            )
            
    except Exception as e:
        logger.error(f"Error stopping tracking for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось остановить отслеживание\n\n"
            f"Ошибка: {str(e)}"
        )


async def my_trackings_callback(callback: CallbackQuery) -> None:
    """Handle my trackings callback."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} requested trackings")

    # Delete main menu message
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

    # TODO: Call GetUserTrackingsUseCase
    text = (
        "📊 <b>Мои отслеживания</b>\n\n"
        "У вас нет отслеживаемых аккаунтов\n\n"
        "💡 Чтобы добавить аккаунт:\n"
        "1. Найдите профиль через /instagram @username\n"
        "2. Нажмите кнопку 📊 Отслеживать\n"
        "3. Выберите что отслеживать (Stories, Posts и т.д.)\n"
        "4. Настройте интервал проверки\n\n"
        "🔔 Вы будете получать уведомления о новом контенте!"
    )

    await callback.message.answer(text)


# Audience tracking (premium feature)

async def handle_audience_payment(callback: CallbackQuery) -> None:
    """Handle audience tracking payment."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: track_audience_{user_id}_{username}
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"User {callback.from_user.id} requested audience tracking for {username}")

    text = (
        f"📊 <b>Audience Tracking для @{username}</b>\n\n"
        "🔥 Премиум функция:\n"
        "• Детальная аналитика подписчиков\n"
        "• Отслеживание новых подписчиков\n"
        "• Отслеживание отписавшихся\n"
        "• История изменений\n\n"
        "💰 Стоимость: 99 Stars (разовый платеж)\n\n"
        "Оплатить?"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить 99 Stars", callback_data=f"audience_pay_{user_id}_{username}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_track_{user_id}_{username}")]
    ])

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def handle_audience_precheckout(callback: CallbackQuery) -> None:
    """Handle audience tracking pre-checkout."""
    # TODO: Implement Stars payment pre-checkout
    pass


async def handle_audience_successful_payment(callback: CallbackQuery) -> None:
    """Handle successful audience tracking payment."""
    # TODO: Activate audience tracking
    # TODO: Call StartAudienceTrackingUseCase
    pass


def register_tracking_handlers(dp: Dispatcher) -> None:
    """Register tracking handlers."""
    # Main tracking callbacks
    dp.callback_query.register(tracking_start_callback, F.data.startswith("ig_track_"))
    dp.callback_query.register(handle_tracking_type_selection, F.data.startswith("track_type_"))
    dp.callback_query.register(handle_tracking_interval_set, F.data.startswith("track_interval_"))
    dp.callback_query.register(handle_tracking_disable_single, F.data.startswith("track_disable_"))
    dp.callback_query.register(handle_tracking_menu_back, F.data.startswith("track_menu_"))
    dp.callback_query.register(tracking_stop_callback, F.data.startswith("unsubscribe_tracking_"))
    dp.callback_query.register(my_trackings_callback, F.data == "my_trackings")
    
    # Audience tracking callbacks
    dp.callback_query.register(handle_audience_payment, F.data.startswith("track_audience_"))
    dp.callback_query.register(handle_audience_precheckout, F.data.startswith("audience_pay_"))

    logger.info("Tracking handlers registered")

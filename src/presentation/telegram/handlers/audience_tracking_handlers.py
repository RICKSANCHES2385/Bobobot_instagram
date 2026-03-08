"""Audience Tracking handlers for Telegram bot."""

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.application.audience_tracking.dtos import CreateAudienceTrackingDTO
from src.domain.audience_tracking.exceptions import (
    DuplicateTrackingException,
    FollowerLimitExceededException,
)
from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container

logger = get_logger(__name__)


def get_audience_tracking_keyboard(user_id: str, username: str) -> InlineKeyboardMarkup:
    """Get audience tracking menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💳 Оплатить 576 ⭐",
            callback_data=f"audience_pay_stars_{user_id}_{username}"
        )],
        [InlineKeyboardButton(
            text="💳 Оплатить 129₽",
            callback_data=f"audience_pay_rub_{user_id}_{username}"
        )],
        [InlineKeyboardButton(
            text="ℹ️ Подробнее",
            callback_data=f"audience_info_{user_id}_{username}"
        )],
        [InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"ig_track_{user_id}_{username}"
        )]
    ])


def get_my_audience_trackings_keyboard() -> InlineKeyboardMarkup:
    """Get my audience trackings keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
    ])


async def show_audience_tracking_offer(callback: CallbackQuery, user_id: str, username: str) -> None:
    """Show audience tracking offer."""
    # Get price
    container = get_container()
    use_cases = container.get_use_cases()
    
    try:
        price_stars = await use_cases.calculate_audience_tracking_price.execute("XTR")
        price_rub = await use_cases.calculate_audience_tracking_price.execute("RUB")
    except Exception as e:
        logger.error(f"Error calculating price: {e}")
        price_stars = None
        price_rub = None
    
    text = (
        f"📊 <b>Audience Tracking для @{username}</b>\n\n"
        "🔥 <b>Премиум функция - отслеживание аудитории</b>\n\n"
        "Что вы получите:\n"
        "• 👥 Отслеживание подписчиков (Followers)\n"
        "• 👤 Отслеживание подписок (Following)\n"
        "• 📈 Уведомления об изменениях\n"
        "• 📊 Детальная статистика\n"
        "• 🔔 Мгновенные уведомления\n\n"
        "⚠️ <b>Ограничение:</b> Аккаунты с >100,000 подписчиков не поддерживаются\n\n"
    )
    
    if price_stars and price_rub:
        text += (
            f"💰 <b>Стоимость:</b>\n"
            f"• {price_stars.formatted} (Telegram Stars)\n"
            f"• {price_rub.formatted}\n\n"
            "📅 Подписка на 30 дней"
        )
    else:
        text += "💰 <b>Стоимость:</b> 576 ⭐ или 129₽\n📅 Подписка на 30 дней"
    
    keyboard = get_audience_tracking_keyboard(user_id, username)
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def handle_audience_tracking_request(callback: CallbackQuery) -> None:
    """Handle audience tracking request - show offer."""
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

    await show_audience_tracking_offer(callback, user_id, username)


async def handle_audience_info(callback: CallbackQuery) -> None:
    """Handle audience tracking info request."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: audience_info_{user_id}_{username}
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    text = (
        "📊 <b>Audience Tracking - Подробная информация</b>\n\n"
        "<b>Что это?</b>\n"
        "Премиум функция для детального отслеживания аудитории Instagram аккаунта.\n\n"
        "<b>Как работает?</b>\n"
        "• Бот регулярно проверяет количество подписчиков и подписок\n"
        "• При изменениях вы получаете уведомление\n"
        "• Видите точное количество новых/ушедших подписчиков\n\n"
        "<b>Ограничения:</b>\n"
        "• Аккаунты с >100,000 подписчиков не поддерживаются\n"
        "• Один аккаунт = одна подписка\n"
        "• Подписка действует 30 дней\n\n"
        "<b>Цена:</b>\n"
        "• 576 Telegram Stars\n"
        "• 129 рублей\n"
        "• Поддержка USDT/TON\n\n"
        "<b>Автопродление:</b>\n"
        "Можно включить после активации подписки"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💳 Оплатить",
            callback_data=f"track_audience_{user_id}_{username}"
        )],
        [InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"track_audience_{user_id}_{username}"
        )]
    ])

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def handle_audience_payment_stars(callback: CallbackQuery) -> None:
    """Handle audience tracking payment with Stars."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    # Parse: audience_pay_stars_{user_id}_{username}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = int(parts[3])
    username = parts[4]

    logger.info(f"User {user_id} initiating Stars payment for audience tracking @{username}")

    # Get container
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Check if tracking already exists
        trackings = await use_cases.get_audience_tracking_status.execute(user_id)
        existing = next((t for t in trackings if t.target_username == username and t.is_active), None)
        
        if existing:
            await callback.message.answer(
                f"ℹ️ У вас уже есть активная подписка на отслеживание @{username}\n\n"
                f"Истекает: {existing.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"Осталось дней: {existing.days_remaining}"
            )
            return

        # TODO: Create Stars invoice
        # For now, show placeholder
        text = (
            f"💳 <b>Оплата Audience Tracking</b>\n\n"
            f"Аккаунт: @{username}\n"
            f"Стоимость: 576 ⭐\n"
            f"Период: 30 дней\n\n"
            "⚠️ Интеграция с Telegram Stars в разработке\n\n"
            "Используйте альтернативный способ оплаты (129₽)"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="💳 Оплатить 129₽",
                callback_data=f"audience_pay_rub_{user_id}_{username}"
            )],
            [InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"track_audience_{user_id}_{username}"
            )]
        ])

        await callback.message.edit_text(text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        await callback.message.answer(
            f"❌ Ошибка при создании платежа\n\n{str(e)}"
        )


async def handle_audience_payment_rub(callback: CallbackQuery) -> None:
    """Handle audience tracking payment with RUB."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    # Parse: audience_pay_rub_{user_id}_{username}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = int(parts[3])
    username = parts[4]

    logger.info(f"User {user_id} initiating RUB payment for audience tracking @{username}")

    text = (
        f"💳 <b>Оплата Audience Tracking</b>\n\n"
        f"Аккаунт: @{username}\n"
        f"Стоимость: 129₽\n"
        f"Период: 30 дней\n\n"
        "⚠️ Интеграция с платежными системами в разработке\n\n"
        "Свяжитесь с поддержкой для активации: @support"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"track_audience_{user_id}_{username}"
        )]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)


async def handle_my_audience_trackings(callback: CallbackQuery) -> None:
    """Handle my audience trackings request."""
    if not callback.from_user:
        return

    await callback.answer()

    user_id = callback.from_user.id
    logger.info(f"User {user_id} requested audience trackings")

    # Get container
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        trackings = await use_cases.get_audience_tracking_status.execute(user_id)

        if not trackings:
            text = (
                "📊 <b>Мои Audience Trackings</b>\n\n"
                "У вас нет активных подписок на отслеживание аудитории\n\n"
                "💡 Чтобы добавить:\n"
                "1. Найдите профиль через /instagram @username\n"
                "2. Нажмите 📊 Отслеживать\n"
                "3. Выберите 👥 Audience Tracking\n"
                "4. Оплатите подписку\n\n"
                "🔔 Вы будете получать уведомления об изменениях аудитории!"
            )
        else:
            text = "📊 <b>Мои Audience Trackings</b>\n\n"
            
            for tracking in trackings:
                status_emoji = "✅" if tracking.is_active and not tracking.is_expired else "❌"
                text += (
                    f"{status_emoji} <b>@{tracking.target_username}</b>\n"
                    f"├ Статус: {'Активна' if tracking.is_active and not tracking.is_expired else 'Неактивна'}\n"
                    f"├ Истекает: {tracking.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
                    f"├ Осталось: {tracking.days_remaining} дн.\n"
                )
                
                if tracking.last_follower_count is not None:
                    text += f"├ Подписчиков: {tracking.last_follower_count:,}\n"
                if tracking.last_following_count is not None:
                    text += f"├ Подписок: {tracking.last_following_count:,}\n"
                
                if tracking.last_checked_at:
                    text += f"└ Проверено: {tracking.last_checked_at.strftime('%d.%m %H:%M')}\n"
                
                text += "\n"

        keyboard = get_my_audience_trackings_keyboard()
        
        try:
            await callback.message.edit_text(text, reply_markup=keyboard)
        except Exception:
            await callback.message.answer(text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error getting audience trackings: {e}")
        await callback.message.answer(
            f"❌ Ошибка при получении подписок\n\n{str(e)}"
        )


async def handle_cancel_audience_tracking(callback: CallbackQuery) -> None:
    """Handle cancel audience tracking."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: audience_cancel_{tracking_id}
    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    tracking_id = int(parts[2])
    user_id = callback.from_user.id

    logger.info(f"User {user_id} cancelling audience tracking {tracking_id}")

    # Get container
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        await use_cases.cancel_audience_tracking.execute((tracking_id, "User requested cancellation"))
        
        await callback.answer("✅ Подписка отменена", show_alert=True)
        
        # Refresh list
        await handle_my_audience_trackings(callback)

    except Exception as e:
        logger.error(f"Error cancelling tracking: {e}")
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


def register_audience_tracking_handlers(dp: Dispatcher) -> None:
    """Register audience tracking handlers."""
    # Main audience tracking callbacks
    dp.callback_query.register(
        handle_audience_tracking_request,
        F.data.startswith("track_audience_")
    )
    dp.callback_query.register(
        handle_audience_info,
        F.data.startswith("audience_info_")
    )
    dp.callback_query.register(
        handle_audience_payment_stars,
        F.data.startswith("audience_pay_stars_")
    )
    dp.callback_query.register(
        handle_audience_payment_rub,
        F.data.startswith("audience_pay_rub_")
    )
    dp.callback_query.register(
        handle_my_audience_trackings,
        F.data == "my_audience_trackings"
    )
    dp.callback_query.register(
        handle_cancel_audience_tracking,
        F.data.startswith("audience_cancel_")
    )

    logger.info("Audience tracking handlers registered")

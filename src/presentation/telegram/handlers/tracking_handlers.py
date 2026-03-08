"""Tracking menu handlers for Telegram bot."""

import asyncio
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container
from src.presentation.telegram.keyboards.tracking_menu import (
    get_tracking_menu_keyboard,
    get_tracking_interval_keyboard
)
from src.application.content_tracking.use_cases.start_tracking import StartTrackingCommand
from src.application.content_tracking.use_cases.stop_tracking import StopTrackingUseCase
from src.domain.content_tracking.value_objects.content_type import ContentType
from src.domain.content_tracking.value_objects.check_interval import CheckInterval

logger = get_logger(__name__)


async def get_tracking_status_dict(user_id: int, username: str) -> dict:
    """Get tracking status for all types.
    
    Returns:
        Dict with status for each type:
        {
            'stories': {'active': bool, 'interval': int},
            'posts': {'active': bool, 'interval': int},
            'followers': {'active': bool, 'interval': int},
            'following': {'active': bool, 'interval': int}
        }
    """
    container = get_container()
    use_cases = container.get_use_cases()
    
    try:
        trackings = await use_cases.get_user_trackings.execute(user_id)
        
        # Find tracking for this username
        user_tracking = next((t for t in trackings if t.instagram_username == username), None)
        
        if not user_tracking:
            return {
                'stories': {'active': False, 'interval': None},
                'posts': {'active': False, 'interval': None},
                'followers': {'active': False, 'interval': None},
                'following': {'active': False, 'interval': None},
            }
        
        # Build status dict
        status = {}
        for tracking_type in ['stories', 'posts', 'followers', 'following']:
            # Check if this type is tracked
            is_active = tracking_type in [t.value for t in user_tracking.tracking_types]
            interval = user_tracking.check_interval_hours if is_active else None
            
            status[tracking_type] = {
                'active': is_active,
                'interval': interval
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting tracking status: {e}")
        return {
            'stories': {'active': False, 'interval': None},
            'posts': {'active': False, 'interval': None},
            'followers': {'active': False, 'interval': None},
            'following': {'active': False, 'interval': None},
        }


async def show_tracking_menu(
    callback: CallbackQuery,
    user_id: str,
    username: str
) -> None:
    """Show tracking configuration menu."""
    if not callback.message:
        return
    
    await callback.answer()
    
    # Get current tracking status
    tracking_status = await get_tracking_status_dict(callback.from_user.id, username)
    
    # Build text
    text = f"🔔 <b>Отслеживание <a href='https://www.instagram.com/{username}/'>{username}</a></b>\n\n"
    text += "Выберите, что хотите отслеживать:\n\n"
    
    # Check if any tracking is active
    any_active = any(status['active'] for status in tracking_status.values())
    
    if any_active:
        text += "✅ Отслеживание активно\n\n"
        text += "Нажмите на кнопку, чтобы изменить настройки"
    else:
        text += "Нажмите на кнопку, чтобы включить отслеживание"
    
    keyboard = get_tracking_menu_keyboard(user_id, username, tracking_status)
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Could not edit message: {e}")
        # Send new message
        await callback.message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


async def handle_tracking_menu(callback: CallbackQuery) -> None:
    """Handle track_menu_{user_id}_{username} callback."""
    if not callback.data or not callback.from_user:
        return
    
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return
    
    user_id = parts[2]
    username = parts[3]
    
    await show_tracking_menu(callback, user_id, username)


async def handle_tracking_type_selection(callback: CallbackQuery) -> None:
    """Handle tracking type selection (stories, posts, followers, following)."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    
    await callback.answer()
    
    # Parse: track_{type}_{user_id}_{username}
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return
    
    tracking_type = parts[1]  # stories, posts, followers, following
    user_id = parts[2]
    username = parts[3]
    
    logger.info(f"User {callback.from_user.id} selected tracking type: {tracking_type} for {username}")
    
    # Get current tracking status
    tracking_status = await get_tracking_status_dict(callback.from_user.id, username)
    current_interval = tracking_status.get(tracking_type, {}).get('interval')
    
    # Check if audience tracking (followers/following)
    if tracking_type in ['followers', 'following']:
        # TODO: Check 100k follower limit
        # TODO: Check if user has paid subscription for audience tracking
        # For now, show interval selection
        pass
    
    # Show interval selection menu
    type_text = {
        'stories': 'историй',
        'posts': 'публикаций',
        'followers': 'подписчиков',
        'following': 'подписок'
    }.get(tracking_type, tracking_type)
    
    text = f"⏰ <b>Интервал проверки {type_text}</b>\n\n"
    text += f"Выберите, как часто проверять новые {type_text} @{username}:"
    
    keyboard = get_tracking_interval_keyboard(user_id, username, tracking_type, current_interval)
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Could not edit message: {e}")
        await callback.message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


async def handle_tracking_interval_set(callback: CallbackQuery) -> None:
    """Handle setting tracking interval."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    
    await callback.answer()
    
    # Parse: track_set_{type}_{user_id}_{username}_{interval}
    parts = callback.data.split("_", 5)
    if len(parts) < 6:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return
    
    tracking_type = parts[2]  # stories, posts, followers, following
    user_id = parts[3]
    username = parts[4]
    interval_str = parts[5]  # 1h, 6h, 12h, 24h
    
    # Convert interval to hours
    interval_map = {"1h": 1, "6h": 6, "12h": 12, "24h": 24}
    interval_hours = interval_map.get(interval_str)
    
    if not interval_hours:
        await callback.answer("❌ Неверный интервал", show_alert=True)
        return
    
    logger.info(f"User {callback.from_user.id} setting tracking: {tracking_type} for {username} every {interval_hours}h")
    
    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()
    
    try:
        # Map tracking type to domain enum
        type_map = {
            'stories': TrackingType.STORIES,
            'posts': TrackingType.POSTS,
            'followers': TrackingType.FOLLOWERS,
            'following': TrackingType.FOLLOWING
        }
        
        domain_type = type_map.get(tracking_type)
        if not domain_type:
            await callback.answer("❌ Неверный тип отслеживания", show_alert=True)
            return
        
        # Create tracking
        command = StartTrackingCommand(
            user_id=callback.from_user.id,
            instagram_username=username,
            tracking_types=[domain_type],
            check_interval_hours=interval_hours
        )
        
        await use_cases.start_tracking.execute(command)
        
        # Show success message
        type_text = {
            'stories': 'историй',
            'posts': 'публикаций',
            'followers': 'подписчиков',
            'following': 'подписок'
        }.get(tracking_type, tracking_type)
        
        interval_text = {
            1: "каждый час",
            6: "каждые 6 часов",
            12: "каждые 12 часов",
            24: "раз в день",
        }.get(interval_hours, f"каждые {interval_hours} часов")
        
        text = f"✅ Отслеживание {type_text} @{username} включено!\n\n"
        text += f"⏰ Интервал проверки: {interval_text}\n\n"
        text += f"Вы будете получать уведомления о новых {type_text}."
        
        await callback.message.edit_text(text, parse_mode="HTML")
        
        # Show tracking menu again after 2 seconds
        await asyncio.sleep(2)
        await show_tracking_menu(callback, user_id, username)
        
    except Exception as e:
        logger.error(f"Error setting tracking: {e}")
        await callback.message.edit_text(
            f"❌ Не удалось включить отслеживание\n\n"
            f"Ошибка: {str(e)}",
            parse_mode="HTML"
        )


async def handle_tracking_disable_single(callback: CallbackQuery) -> None:
    """Handle disabling single tracking type."""
    if not callback.data or not callback.from_user or not callback.message:
        return
    
    await callback.answer()
    
    # Parse: track_disable_single_{type}_{user_id}_{username}
    parts = callback.data.split("_", 5)
    if len(parts) < 6:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return
    
    tracking_type = parts[3]  # stories, posts, followers, following
    user_id = parts[4]
    username = parts[5]
    
    logger.info(f"User {callback.from_user.id} disabling tracking: {tracking_type} for {username}")
    
    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()
    
    try:
        # Map tracking type to domain enum
        type_map = {
            'stories': TrackingType.STORIES,
            'posts': TrackingType.POSTS,
            'followers': TrackingType.FOLLOWERS,
            'following': TrackingType.FOLLOWING
        }
        
        domain_type = type_map.get(tracking_type)
        if not domain_type:
            await callback.answer("❌ Неверный тип отслеживания", show_alert=True)
            return
        
        # Get current tracking
        trackings = await use_cases.get_user_trackings.execute(callback.from_user.id)
        user_tracking = next((t for t in trackings if t.instagram_username == username), None)
        
        if not user_tracking:
            await callback.answer("❌ Отслеживание не найдено", show_alert=True)
            return
        
        # Stop tracking
        command = StopTrackingCommand(tracking_id=user_tracking.id)
        await use_cases.stop_tracking.execute(command)
        
        # Show success message
        type_text = {
            'stories': 'историй',
            'posts': 'публикаций',
            'followers': 'подписчиков',
            'following': 'подписок'
        }.get(tracking_type, tracking_type)
        
        text = f"🔕 Отслеживание {type_text} @{username} отключено"
        
        await callback.message.edit_text(text, parse_mode="HTML")
        
        # Show tracking menu again after 2 seconds
        await asyncio.sleep(2)
        await show_tracking_menu(callback, user_id, username)
        
    except Exception as e:
        logger.error(f"Error disabling tracking: {e}")
        await callback.message.edit_text(
            f"❌ Не удалось отключить отслеживание\n\n"
            f"Ошибка: {str(e)}",
            parse_mode="HTML"
        )


def register_tracking_handlers(dp: Dispatcher) -> None:
    """Register tracking handlers."""
    # Tracking menu
    dp.callback_query.register(handle_tracking_menu, F.data.startswith("track_menu_"))
    
    # Type selection
    dp.callback_query.register(handle_tracking_type_selection, F.data.startswith("track_stories_"))
    dp.callback_query.register(handle_tracking_type_selection, F.data.startswith("track_posts_"))
    dp.callback_query.register(handle_tracking_type_selection, F.data.startswith("track_followers_"))
    dp.callback_query.register(handle_tracking_type_selection, F.data.startswith("track_following_"))
    
    # Interval set
    dp.callback_query.register(handle_tracking_interval_set, F.data.startswith("track_set_"))
    
    # Disable
    dp.callback_query.register(handle_tracking_disable_single, F.data.startswith("track_disable_single_"))

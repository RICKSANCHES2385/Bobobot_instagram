"""Tracking menu keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_tracking_menu_keyboard(
    user_id: str,
    username: str,
    tracking_status: dict
) -> InlineKeyboardMarkup:
    """Get tracking configuration menu keyboard with dynamic status.
    
    Args:
        user_id: Instagram user ID
        username: Instagram username
        tracking_status: Dict with status for each type
            {
                'stories': {'active': bool, 'interval': int},
                'posts': {'active': bool, 'interval': int},
                'followers': {'active': bool, 'interval': int},
                'following': {'active': bool, 'interval': int}
            }
    
    Returns:
        Keyboard markup
    """
    def get_status_text(type_status: dict) -> str:
        """Get status text for tracking type."""
        if type_status.get('active') and type_status.get('interval'):
            interval = type_status['interval']
            interval_text = {
                1: "каждый час",
                6: "каждые 6 часов",
                12: "каждые 12 часов",
                24: "раз в день",
            }.get(interval, "активно")
            return f"✅ {interval_text}"
        return "выключено"
    
    keyboard = [
        # Row 1: Stories tracking
        [
            InlineKeyboardButton(
                text=f"📖 Истории: {get_status_text(tracking_status.get('stories', {}))}",
                callback_data=f"track_stories_{user_id}_{username}"
            ),
        ],
        # Row 2: Posts tracking
        [
            InlineKeyboardButton(
                text=f"📷 Публикации: {get_status_text(tracking_status.get('posts', {}))}",
                callback_data=f"track_posts_{user_id}_{username}"
            ),
        ],
        # Row 3: Followers tracking
        [
            InlineKeyboardButton(
                text=f"👥 Подписчики: {get_status_text(tracking_status.get('followers', {}))}",
                callback_data=f"track_followers_{user_id}_{username}"
            ),
        ],
        # Row 4: Following tracking
        [
            InlineKeyboardButton(
                text=f"➕ Подписки: {get_status_text(tracking_status.get('following', {}))}",
                callback_data=f"track_following_{user_id}_{username}"
            ),
        ],
        # Back button
        [
            InlineKeyboardButton(
                text="◀️ Назад к профилю",
                callback_data=f"ig_back_{user_id}_{username}"
            ),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tracking_interval_keyboard(
    user_id: str,
    username: str,
    tracking_type: str,
    current_interval: int = None
) -> InlineKeyboardMarkup:
    """Get tracking interval selection keyboard.
    
    Args:
        user_id: Instagram user ID
        username: Instagram username
        tracking_type: Type of tracking (stories, posts, followers, following)
        current_interval: Current interval in hours (if tracking is active)
    
    Returns:
        Keyboard markup
    """
    def get_button_text(interval_hours: int, label: str) -> str:
        """Get button text with checkmark if selected."""
        if current_interval == interval_hours:
            return f"✅ {label}"
        return f"⏰ {label}"
    
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_button_text(1, "Каждый час"),
                callback_data=f"track_set_{tracking_type}_{user_id}_{username}_1h"
            ),
            InlineKeyboardButton(
                text=get_button_text(6, "Каждые 6 часов"),
                callback_data=f"track_set_{tracking_type}_{user_id}_{username}_6h"
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_button_text(12, "Каждые 12 часов"),
                callback_data=f"track_set_{tracking_type}_{user_id}_{username}_12h"
            ),
            InlineKeyboardButton(
                text=get_button_text(24, "Раз в день"),
                callback_data=f"track_set_{tracking_type}_{user_id}_{username}_24h"
            ),
        ],
    ]
    
    # Add disable button if tracking is active
    if current_interval:
        keyboard.append([
            InlineKeyboardButton(
                text="🔕 Отключить",
                callback_data=f"track_disable_single_{tracking_type}_{user_id}_{username}"
            ),
        ])
    
    # Cancel button
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=f"track_menu_{user_id}_{username}"
        ),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

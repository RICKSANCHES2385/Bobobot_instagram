"""Instagram action keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_profile_keyboard(user_id: str, username: str) -> InlineKeyboardMarkup:
    """Get profile action keyboard.
    
    Args:
        user_id: Instagram user ID
        username: Instagram username
    
    Layout:
    👀 Посмотреть истории
    ⭐ Highlights | 📷 Публикации
    🎬 Reels | 📝 Отметки
    📊 Отслеживать
    """
    keyboard = [
        # Main action button - View stories (full width)
        [
            InlineKeyboardButton(
                text="👀 Посмотреть истории",
                callback_data=f"ig_stories_{user_id}_{username}"
            ),
        ],
        # Row 1: Highlights and Posts (2 columns)
        [
            InlineKeyboardButton(
                text="⭐ Highlights",
                callback_data=f"ig_highlights_{user_id}_{username}"
            ),
            InlineKeyboardButton(
                text="📷 Публикации",
                callback_data=f"ig_posts_{user_id}_{username}"
            ),
        ],
        # Row 2: Reels and Tags (2 columns)
        [
            InlineKeyboardButton(
                text="🎬 Reels",
                callback_data=f"ig_reels_{user_id}_{username}"
            ),
            InlineKeyboardButton(
                text="📝 Отметки",
                callback_data=f"ig_tagged_{user_id}_{username}"
            ),
        ],
        # Row 3: Track (full width)
        [
            InlineKeyboardButton(
                text="📊 Отслеживать",
                callback_data=f"ig_track_{user_id}_{username}"
            ),
        ],
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_profile_keyboard(user_id: str, username: str) -> InlineKeyboardMarkup:
    """Get back to profile keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="◀️ Назад к профилю",
                callback_data=f"ig_back_{user_id}_{username}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

"""Main menu keyboards."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Get start menu keyboard.
    
    Layout:
    👑 Тарифы Безлимит
    🔍 Смотреть сторис/посты
    📊 Мои отслеживания
    👥 Партнёрка | 🏛 Поддержка
    """
    keyboard = [
        # Row 1: Tariffs button (full width)
        [
            InlineKeyboardButton(
                text="👑 Тарифы Безлимит",
                callback_data="tariffs_menu"
            )
        ],
        # Row 2: View stories/posts (full width)
        [
            InlineKeyboardButton(
                text="🔍 Смотреть сторис/посты",
                callback_data="view_content"
            )
        ],
        # Row 3: My trackings (full width)
        [
            InlineKeyboardButton(
                text="📊 Мои отслеживания",
                callback_data="my_trackings"
            )
        ],
        # Row 4: Partnership and Support (two buttons)
        [
            InlineKeyboardButton(text="👥 Партнёрка", callback_data="partnership"),
            InlineKeyboardButton(text="🏛 Поддержка", callback_data="support")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

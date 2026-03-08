"""Instagram handlers for Telegram bot."""

import re
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.keyboards.instagram_menu import get_profile_keyboard, get_back_to_profile_keyboard

logger = get_logger(__name__)


def parse_instagram_username(text: str) -> Optional[str]:
    """Parse Instagram username from text or URL."""
    # Remove @ prefix
    text = text.strip().lstrip("@")
    
    # Try to extract from URL patterns
    url_patterns = [
        r"instagram\.com/([a-zA-Z0-9._]+)",
        r"instagr\.am/([a-zA-Z0-9._]+)",
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).rstrip("/")
    
    # If not URL, treat as username (validate format)
    if re.match(r"^[a-zA-Z0-9._]+$", text):
        return text
    
    return None


async def send_user_profile(message: Message, username: str, user_id: str) -> None:
    """Send Instagram profile information."""
    # TODO: Call FetchInstagramProfileUseCase
    # TODO: Format profile with profile_formatter
    
    text = (
        f"👤 <b>@{username}</b>\n\n"
        "📊 Статистика:\n"
        "• Публикаций: 0\n"
        "• Подписчиков: 0\n"
        "• Подписок: 0\n\n"
        "📝 Описание профиля\n\n"
        "🔔 Отслеживание: не активно"
    )
    
    keyboard = get_profile_keyboard(user_id, username)
    await message.answer(text, reply_markup=keyboard)


async def instagram_profile_handler(message: Message) -> None:
    """Handle Instagram username/link message."""
    if not message.from_user or not message.text:
        return

    username = parse_instagram_username(message.text)
    if not username:
        await message.answer(
            "❌ Неверный формат username или ссылки\n\n"
            "Примеры:\n"
            "• cristiano\n"
            "• @cristiano\n"
            "• https://instagram.com/cristiano"
        )
        return

    logger.info(f"User {message.from_user.id} requested profile: {username}")
    
    # TODO: Check subscription via CheckSubscriptionStatusUseCase
    # TODO: Check rate limits
    
    await message.answer(f"🔍 Получаю информацию о @{username}...")
    await send_user_profile(message, username, str(message.from_user.id))


async def show_profile_from_callback(callback: CallbackQuery, user_id: str, username: str) -> None:
    """Show profile from callback."""
    if not callback.message:
        return
    
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")
    
    await send_user_profile(callback.message, username, user_id)


async def handle_profile_callback(callback: CallbackQuery) -> None:
    """Handle ig_profile_{user_id}_{username} callback."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    await show_profile_from_callback(callback, user_id, username)


async def handle_back_to_profile(callback: CallbackQuery) -> None:
    """Handle ig_back_{user_id}_{username} callback."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    await show_profile_from_callback(callback, user_id, username)


# Content handlers

async def handle_stories(callback: CallbackQuery) -> None:
    """Handle stories callback - load stories in batches of 3."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching stories for {username} (user_id={user_id})")

    # TODO: Call FetchInstagramStoriesUseCase
    # TODO: Send stories in batches of 3
    
    await callback.message.answer(
        f"📖 <b>Stories @{username}</b>\n\n"
        "У пользователя нет активных историй",
        reply_markup=get_back_to_profile_keyboard(user_id, username)
    )


async def handle_stories_next(callback: CallbackQuery) -> None:
    """Handle next batch of stories."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: ig_stories_next_{user_id}_{username}_{offset}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]
    offset = int(parts[5]) if len(parts) > 5 else 3

    logger.info(f"Fetching next stories for {username} (offset={offset})")

    # TODO: Load next batch
    await callback.answer("Загружаю следующие истории...")


async def handle_posts(callback: CallbackQuery) -> None:
    """Handle posts callback - load posts in batches of 5."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching posts for {username} (user_id={user_id})")

    # TODO: Call FetchInstagramPostsUseCase
    # TODO: Send posts in batches of 5
    
    await callback.message.answer(
        f"📸 <b>Posts @{username}</b>\n\n"
        "Загружаю публикации...",
        reply_markup=get_back_to_profile_keyboard(user_id, username)
    )


async def handle_posts_next(callback: CallbackQuery) -> None:
    """Handle next batch of posts."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: ig_posts_next_{user_id}_{username}_{offset}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]
    offset = int(parts[5]) if len(parts) > 5 else 5

    logger.info(f"Fetching next posts for {username} (offset={offset})")

    # TODO: Load next batch
    await callback.answer("Загружаю следующие публикации...")


async def handle_reels(callback: CallbackQuery) -> None:
    """Handle reels callback - load reels in batches of 3."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching reels for {username} (user_id={user_id})")

    # TODO: Call FetchInstagramReelsUseCase
    # TODO: Send reels in batches of 3
    
    await callback.message.answer(
        f"🎬 <b>Reels @{username}</b>\n\n"
        "Загружаю reels...",
        reply_markup=get_back_to_profile_keyboard(user_id, username)
    )


async def handle_reels_next(callback: CallbackQuery) -> None:
    """Handle next batch of reels."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: ig_reels_next_{user_id}_{username}_{offset}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]
    offset = int(parts[5]) if len(parts) > 5 else 3

    logger.info(f"Fetching next reels for {username} (offset={offset})")

    # TODO: Load next batch
    await callback.answer("Загружаю следующие reels...")


async def handle_highlights(callback: CallbackQuery) -> None:
    """Handle highlights callback - show list of highlights."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching highlights for {username} (user_id={user_id})")

    # TODO: Call FetchInstagramHighlightsUseCase
    
    await callback.message.answer(
        f"⭐ <b>Highlights @{username}</b>\n\n"
        "У пользователя нет highlights",
        reply_markup=get_back_to_profile_keyboard(user_id, username)
    )


async def handle_highlight_view(callback: CallbackQuery) -> None:
    """Handle viewing specific highlight."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: ig_highlight_{highlight_id}_{user_id}_{username}
    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    highlight_id = parts[2]
    user_id = parts[3]
    username = parts[4]

    logger.info(f"Viewing highlight {highlight_id} for {username}")

    # TODO: Load highlight stories
    await callback.answer("Загружаю highlight...")


async def handle_tagged(callback: CallbackQuery) -> None:
    """Handle tagged posts callback."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching tagged posts for {username}")

    # TODO: Call FetchInstagramTaggedPostsUseCase
    
    await callback.message.answer(
        f"🏷 <b>Tagged @{username}</b>\n\n"
        "Загружаю отмеченные публикации...",
        reply_markup=get_back_to_profile_keyboard(user_id, username)
    )


# Social handlers

async def handle_followers(callback: CallbackQuery) -> None:
    """Handle followers callback - show first 50."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching followers for {username}")

    # TODO: Call FetchInstagramFollowersUseCase (limit 50)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать всех", callback_data=f"ig_followers_dl_{user_id}_{username}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_back_{user_id}_{username}")]
    ])
    
    await callback.message.answer(
        f"👥 <b>Подписчики @{username}</b>\n\n"
        "Первые 50 подписчиков:\n"
        "Загружаю...",
        reply_markup=keyboard
    )


async def handle_followers_download(callback: CallbackQuery) -> None:
    """Handle download all followers as txt."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer("Подготавливаю файл...")

    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]

    logger.info(f"Downloading all followers for {username}")

    # TODO: Call FetchInstagramFollowersUseCase (all)
    # TODO: Format as txt file
    # TODO: Send as document
    
    await callback.message.answer("⏳ Загружаю всех подписчиков, это может занять время...")


async def handle_following(callback: CallbackQuery) -> None:
    """Handle following callback - show first 50."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching following for {username}")

    # TODO: Call FetchInstagramFollowingUseCase (limit 50)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Скачать всех", callback_data=f"ig_following_dl_{user_id}_{username}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_back_{user_id}_{username}")]
    ])
    
    await callback.message.answer(
        f"👤 <b>Подписки @{username}</b>\n\n"
        "Первые 50 подписок:\n"
        "Загружаю...",
        reply_markup=keyboard
    )


async def handle_following_download(callback: CallbackQuery) -> None:
    """Handle download all following as txt."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer("Подготавливаю файл...")

    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]

    logger.info(f"Downloading all following for {username}")

    # TODO: Call FetchInstagramFollowingUseCase (all)
    # TODO: Format as txt file
    # TODO: Send as document
    
    await callback.message.answer("⏳ Загружаю все подписки, это может занять время...")


# Download handlers

async def handle_posts_download(callback: CallbackQuery) -> None:
    """Handle download all posts list as txt."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer("Подготавливаю файл...")

    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]

    logger.info(f"Downloading posts list for {username}")

    # TODO: Call FetchInstagramPostsUseCase (all)
    # TODO: Format as txt file with links
    # TODO: Send as document
    
    await callback.message.answer("⏳ Подготавливаю список всех публикаций...")


async def handle_reels_download(callback: CallbackQuery) -> None:
    """Handle download all reels list as txt."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer("Подготавливаю файл...")

    parts = callback.data.split("_", 4)
    if len(parts) < 5:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[3]
    username = parts[4]

    logger.info(f"Downloading reels list for {username}")

    # TODO: Call FetchInstagramReelsUseCase (all)
    # TODO: Format as txt file with links
    # TODO: Send as document
    
    await callback.message.answer("⏳ Подготавливаю список всех reels...")


def register_instagram_handlers(dp: Dispatcher) -> None:
    """Register Instagram handlers."""
    # Profile callbacks
    dp.callback_query.register(handle_profile_callback, F.data.startswith("ig_profile_"))
    dp.callback_query.register(handle_back_to_profile, F.data.startswith("ig_back_"))
    
    # Content callbacks
    dp.callback_query.register(handle_stories, F.data.startswith("ig_stories_"))
    dp.callback_query.register(handle_stories_next, F.data.startswith("ig_stories_next_"))
    dp.callback_query.register(handle_posts, F.data.startswith("ig_posts_"))
    dp.callback_query.register(handle_posts_next, F.data.startswith("ig_posts_next_"))
    dp.callback_query.register(handle_reels, F.data.startswith("ig_reels_"))
    dp.callback_query.register(handle_reels_next, F.data.startswith("ig_reels_next_"))
    dp.callback_query.register(handle_highlights, F.data.startswith("ig_highlights_"))
    dp.callback_query.register(handle_highlight_view, F.data.startswith("ig_highlight_"))
    dp.callback_query.register(handle_tagged, F.data.startswith("ig_tagged_"))
    
    # Social callbacks
    dp.callback_query.register(handle_followers, F.data.startswith("ig_followers_"))
    dp.callback_query.register(handle_followers_download, F.data.startswith("ig_followers_dl_"))
    dp.callback_query.register(handle_following, F.data.startswith("ig_following_"))
    dp.callback_query.register(handle_following_download, F.data.startswith("ig_following_dl_"))
    
    # Download callbacks
    dp.callback_query.register(handle_posts_download, F.data.startswith("ig_posts_dl_"))
    dp.callback_query.register(handle_reels_download, F.data.startswith("ig_reels_dl_"))

    logger.info("Instagram handlers registered")

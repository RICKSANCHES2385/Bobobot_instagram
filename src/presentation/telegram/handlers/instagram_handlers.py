"""Instagram handlers for Telegram bot."""

import re
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container
from src.presentation.telegram.keyboards.instagram_menu import get_profile_keyboard, get_back_to_profile_keyboard
from src.presentation.telegram.formatters.profile_formatter import format_profile_text, format_tracking_status
from src.application.instagram_integration.use_cases.fetch_instagram_stories import FetchInstagramStoriesCommand
from src.application.instagram_integration.use_cases.fetch_instagram_posts import FetchInstagramPostsCommand
from src.application.instagram_integration.use_cases.fetch_instagram_reels import FetchInstagramReelsCommand
from src.application.instagram_integration.use_cases.fetch_instagram_followers import FetchInstagramFollowersCommand
from src.application.instagram_integration.use_cases.fetch_instagram_following import FetchInstagramFollowingCommand
from src.presentation.telegram.media.media_downloader import MediaDownloader
from src.presentation.telegram.media.media_sender import MediaSender

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
    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()
    
    try:
        # Fetch Instagram profile
        profile = await use_cases.fetch_instagram_profile.execute(username)
        
        # Check tracking status
        try:
            trackings = await use_cases.get_user_trackings.execute(int(user_id))
            tracking = next((t for t in trackings if t.instagram_username == username), None)
            tracking_status = format_tracking_status(tracking) if tracking else "🔔 Отслеживание: не активно"
        except Exception as e:
            logger.warning(f"Could not get tracking status: {e}")
            tracking_status = "🔔 Отслеживание: не активно"
        
        # Format profile text
        text = format_profile_text(
            username=profile.username,
            full_name=profile.full_name,
            biography=profile.bio,
            followers_count=profile.followers,
            following_count=profile.following,
            posts_count=profile.posts,
            is_private=profile.is_private,
            is_verified=profile.is_verified,
            is_business=False,  # Not in DTO
            external_url=profile.external_url,
        )
        
        # Add tracking status
        text = f"{text}\n{tracking_status}"
        
        keyboard = get_profile_keyboard(user_id, username)
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error fetching profile {username}: {e}")
        await message.answer(
            f"❌ Не удалось получить профиль @{username}\n\n"
            "Возможные причины:\n"
            "• Профиль не существует\n"
            "• Профиль закрыт\n"
            "• Временная ошибка Instagram API\n\n"
            "Попробуйте позже или проверьте правильность username"
        )


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

    user_id = message.from_user.id
    logger.info(f"User {user_id} requested profile: {username}")
    
    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()
    
    try:
        # Check subscription status
        sub_status = await use_cases.check_subscription_status.execute(user_id)
        if not sub_status.is_active:
            await message.answer(
                "❌ Для просмотра профилей нужна активная подписка\n\n"
                "Используйте /buy для покупки подписки"
            )
            return
    except Exception as e:
        logger.error(f"Error checking subscription for user {user_id}: {e}")
        # Continue anyway for now
    
    await message.answer(f"🔍 Получаю информацию о @{username}...")
    await send_user_profile(message, username, str(user_id))


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
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching stories for {username} (user_id={user_id})")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # First, get profile to get Instagram user_id
        profile = await use_cases.fetch_instagram_profile.execute(username)
        
        # Fetch stories using Instagram user_id
        command = FetchInstagramStoriesCommand(username=username, user_id=profile.user_id)
        stories = await use_cases.fetch_instagram_stories.execute(command)
        
        if not stories:
            await callback.message.answer(
                f"📖 <b>Stories @{username}</b>\n\n"
                "У пользователя нет активных историй",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            return
        
        # Send first batch (3 stories)
        from src.presentation.telegram.formatters.content_formatter import format_story_caption
        
        batch_size = 3
        first_batch = stories[:batch_size]
        
        # Create media handlers for this request
        media_downloader = MediaDownloader()
        media_sender = MediaSender(callback.message.bot)
        
        for story in first_batch:
            caption = format_story_caption(story, username)
            
            # Download and send media
            try:
                file_path = await media_downloader.download_media(story.media_url, story.media_type)
                if file_path:
                    await media_sender.send_media(
                        callback.message,
                        file_path,
                        story.media_type,
                        caption
                    )
                else:
                    await callback.message.answer(caption)
            except Exception as e:
                logger.error(f"Error sending story media: {e}")
                await callback.message.answer(caption)
        
        # Show "Load more" button if there are more stories
        if len(stories) > batch_size:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"📖 Загрузить ещё ({len(stories) - batch_size})",
                    callback_data=f"ig_stories_next_{user_id}_{username}_{batch_size}"
                )],
                [InlineKeyboardButton(
                    text="◀️ Назад к профилю",
                    callback_data=f"ig_back_{user_id}_{username}"
                )]
            ])
            await callback.message.answer(
                f"Показано {batch_size} из {len(stories)} историй",
                reply_markup=keyboard
            )
        else:
            await callback.message.answer(
                "Все истории загружены",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            
    except Exception as e:
        logger.error(f"Error fetching stories for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось загрузить истории @{username}\n\n"
            "Попробуйте позже",
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
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching posts for {username} (user_id={user_id})")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # First, get profile to get Instagram user_id
        profile = await use_cases.fetch_instagram_profile.execute(username)
        
        # Fetch posts using Instagram user_id
        command = FetchInstagramPostsCommand(user_id=profile.user_id, cursor=None)
        posts = await use_cases.fetch_instagram_posts.execute(command)
        
        if not posts:
            await callback.message.answer(
                f"📸 <b>Posts @{username}</b>\n\n"
                "У пользователя нет публикаций",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            return
        
        # Send first batch (5 posts)
        from src.presentation.telegram.formatters.content_formatter import format_post_caption
        
        batch_size = 5
        first_batch = posts[:batch_size]
        
        # Create media handlers for this request
        media_downloader = MediaDownloader()
        media_sender = MediaSender(callback.message.bot)
        
        for post in first_batch:
            caption = format_post_caption(post, username)
            
            # Download and send media
            try:
                if len(post.media_urls) == 1:
                    # Single media
                    file_path = await media_downloader.download_media(post.media_urls[0], post.media_type)
                    if file_path:
                        await media_sender.send_media(
                            callback.message,
                            file_path,
                            post.media_type,
                            caption
                        )
                    else:
                        await callback.message.answer(caption)
                elif len(post.media_urls) > 1:
                    # Media group (album)
                    file_paths = []
                    for url in post.media_urls[:10]:  # Telegram limit: 10 items
                        file_path = await media_downloader.download_media(url, "photo")
                        if file_path:
                            file_paths.append(file_path)
                    
                    if file_paths:
                        await media_sender.send_media_group(
                            callback.message,
                            file_paths,
                            caption
                        )
                    else:
                        await callback.message.answer(caption)
                else:
                    await callback.message.answer(caption)
            except Exception as e:
                logger.error(f"Error sending post media: {e}")
                await callback.message.answer(caption)
        
        # Show "Load more" button if there are more posts
        if len(posts) > batch_size:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"📸 Загрузить ещё ({len(posts) - batch_size})",
                    callback_data=f"ig_posts_next_{user_id}_{username}_{batch_size}"
                )],
                [InlineKeyboardButton(
                    text="◀️ Назад к профилю",
                    callback_data=f"ig_back_{user_id}_{username}"
                )]
            ])
            await callback.message.answer(
                f"Показано {batch_size} из {len(posts)} публикаций",
                reply_markup=keyboard
            )
        else:
            await callback.message.answer(
                "Все публикации загружены",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            
    except Exception as e:
        logger.error(f"Error fetching posts for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось загрузить публикации @{username}\n\n"
            "Попробуйте позже",
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
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching reels for {username} (user_id={user_id})")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # First, get profile to get Instagram user_id
        profile = await use_cases.fetch_instagram_profile.execute(username)
        
        # Fetch reels using Instagram user_id
        command = FetchInstagramReelsCommand(user_id=profile.user_id, cursor=None)
        reels = await use_cases.fetch_instagram_reels.execute(command)
        
        if not reels:
            await callback.message.answer(
                f"🎬 <b>Reels @{username}</b>\n\n"
                "У пользователя нет reels",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            return
        
        # Send first batch (3 reels)
        from src.presentation.telegram.formatters.content_formatter import format_reel_caption
        
        batch_size = 3
        first_batch = reels[:batch_size]
        
        # Create media handlers for this request
        media_downloader = MediaDownloader()
        media_sender = MediaSender(callback.message.bot)
        
        for reel in first_batch:
            caption = format_reel_caption(reel, username)
            
            # Download and send video
            try:
                file_path = await media_downloader.download_media(reel.video_url, "video")
                if file_path:
                    await media_sender.send_media(
                        callback.message,
                        file_path,
                        "video",
                        caption
                    )
                else:
                    await callback.message.answer(caption)
            except Exception as e:
                logger.error(f"Error sending reel video: {e}")
                await callback.message.answer(caption)
        
        # Show "Load more" button if there are more reels
        if len(reels) > batch_size:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=f"🎬 Загрузить ещё ({len(reels) - batch_size})",
                    callback_data=f"ig_reels_next_{user_id}_{username}_{batch_size}"
                )],
                [InlineKeyboardButton(
                    text="◀️ Назад к профилю",
                    callback_data=f"ig_back_{user_id}_{username}"
                )]
            ])
            await callback.message.answer(
                f"Показано {batch_size} из {len(reels)} reels",
                reply_markup=keyboard
            )
        else:
            await callback.message.answer(
                "Все reels загружены",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            
    except Exception as e:
        logger.error(f"Error fetching reels for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось загрузить reels @{username}\n\n"
            "Попробуйте позже",
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
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching highlights for {username} (user_id={user_id})")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Fetch highlights
        highlights = await use_cases.fetch_instagram_highlights.execute(username)
        
        if not highlights:
            await callback.message.answer(
                f"⭐ <b>Highlights @{username}</b>\n\n"
                "У пользователя нет highlights",
                reply_markup=get_back_to_profile_keyboard(user_id, username)
            )
            return
        
        # Show list of highlights
        text = f"⭐ <b>Highlights @{username}</b>\n\n"
        text += f"Всего highlights: {len(highlights)}\n\n"
        
        keyboard_buttons = []
        for highlight in highlights:
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"⭐ {highlight.title} ({highlight.media_count} шт.)",
                    callback_data=f"ig_highlight_{highlight.id}_{user_id}_{username}"
                )
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="◀️ Назад к профилю",
                callback_data=f"ig_back_{user_id}_{username}"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error fetching highlights for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось загрузить highlights @{username}\n\n"
            "Попробуйте позже",
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
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching followers for {username}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # First, get profile to get Instagram user_id
        profile = await use_cases.fetch_instagram_profile.execute(username)
        
        # Fetch first 50 followers
        command = FetchInstagramFollowersCommand(username=username, user_id=profile.user_id, cursor=None)
        result = await use_cases.fetch_instagram_followers.execute(command)
        
        # Format followers list
        from src.presentation.telegram.formatters.list_formatter import format_followers_list
        text = format_followers_list(result.followers, username, result.total_count)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Скачать всех", callback_data=f"ig_followers_dl_{user_id}_{username}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_back_{user_id}_{username}")]
        ])
        
        await callback.message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error fetching followers for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось загрузить подписчиков @{username}\n\n"
            "Попробуйте позже",
            reply_markup=get_back_to_profile_keyboard(user_id, username)
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
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    user_id = parts[2]
    username = parts[3]

    logger.info(f"Fetching following for {username}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # First, get profile to get Instagram user_id
        profile = await use_cases.fetch_instagram_profile.execute(username)
        
        # Fetch first 50 following
        from src.application.instagram_integration.use_cases.fetch_instagram_following import FetchInstagramFollowingCommand
        command = FetchInstagramFollowingCommand(username=username, user_id=profile.user_id, cursor=None)
        result = await use_cases.fetch_instagram_following.execute(command)
        
        # Format following list
        from src.presentation.telegram.formatters.list_formatter import format_following_list
        text = format_following_list(result.following, username, result.total_count)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Скачать всех", callback_data=f"ig_following_dl_{user_id}_{username}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"ig_back_{user_id}_{username}")]
        ])
        
        await callback.message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error fetching following for {username}: {e}")
        await callback.message.answer(
            f"❌ Не удалось загрузить подписки @{username}\n\n"
            "Попробуйте позже",
            reply_markup=get_back_to_profile_keyboard(user_id, username)
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

"""Notification sender for content updates."""

import asyncio
from typing import List, Optional
from aiogram import Bot

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container

logger = get_logger(__name__)


class NotificationSender:
    """Send notifications to users about content updates."""
    
    def __init__(self, bot: Bot):
        """Initialize sender."""
        self.bot = bot
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start notification sender (placeholder for future queue processing)."""
        if self.is_running:
            logger.warning("Notification sender already running")
            return
        
        self.is_running = True
        logger.info("Notification sender started")
    
    async def stop(self):
        """Stop notification sender."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Notification sender stopped")
    
    async def send_story_notification(
        self,
        user_id: int,
        username: str,
        story_count: int
    ):
        """Send notification about new stories.
        
        Args:
            user_id: Telegram user ID
            username: Instagram username
            story_count: Number of new stories
        """
        try:
            text = (
                f"📖 <b>Новые истории!</b>\n\n"
                f"@{username} опубликовал(а) {story_count} "
                f"{'историю' if story_count == 1 else 'истории' if story_count < 5 else 'историй'}\n\n"
                f"Используйте /instagram {username} для просмотра"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent story notification to user {user_id} for @{username}")
            
        except Exception as e:
            logger.error(f"Error sending story notification to {user_id}: {e}")
    
    async def send_post_notification(
        self,
        user_id: int,
        username: str,
        post_count: int
    ):
        """Send notification about new posts.
        
        Args:
            user_id: Telegram user ID
            username: Instagram username
            post_count: Number of new posts
        """
        try:
            text = (
                f"📸 <b>Новые публикации!</b>\n\n"
                f"@{username} опубликовал(а) {post_count} "
                f"{'публикацию' if post_count == 1 else 'публикации' if post_count < 5 else 'публикаций'}\n\n"
                f"Используйте /instagram {username} для просмотра"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent post notification to user {user_id} for @{username}")
            
        except Exception as e:
            logger.error(f"Error sending post notification to {user_id}: {e}")
    
    async def send_followers_notification(
        self,
        user_id: int,
        username: str,
        new_followers: int,
        unfollowers: int
    ):
        """Send notification about followers changes.
        
        Args:
            user_id: Telegram user ID
            username: Instagram username
            new_followers: Number of new followers
            unfollowers: Number of unfollowers
        """
        try:
            changes = []
            if new_followers > 0:
                changes.append(f"+{new_followers} подписчиков")
            if unfollowers > 0:
                changes.append(f"-{unfollowers} отписались")
            
            if not changes:
                return
            
            text = (
                f"👥 <b>Изменения подписчиков!</b>\n\n"
                f"@{username}: {', '.join(changes)}\n\n"
                f"Используйте /instagram {username} для просмотра"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent followers notification to user {user_id} for @{username}")
            
        except Exception as e:
            logger.error(f"Error sending followers notification to {user_id}: {e}")
    
    async def send_following_notification(
        self,
        user_id: int,
        username: str,
        new_following: int,
        unfollowing: int
    ):
        """Send notification about following changes.
        
        Args:
            user_id: Telegram user ID
            username: Instagram username
            new_following: Number of new following
            unfollowing: Number of unfollowing
        """
        try:
            changes = []
            if new_following > 0:
                changes.append(f"+{new_following} подписок")
            if unfollowing > 0:
                changes.append(f"-{unfollowing} отписок")
            
            if not changes:
                return
            
            text = (
                f"👤 <b>Изменения подписок!</b>\n\n"
                f"@{username}: {', '.join(changes)}\n\n"
                f"Используйте /instagram {username} для просмотра"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent following notification to user {user_id} for @{username}")
            
        except Exception as e:
            logger.error(f"Error sending following notification to {user_id}: {e}")

"""Telegram Notification Sender."""

import logging
from typing import Optional

from src.domain.notification.services.notification_sender import INotificationSender
from src.domain.notification.aggregates.notification import Notification


logger = logging.getLogger(__name__)


class TelegramNotificationSender(INotificationSender):
    """Telegram implementation of notification sender."""

    def __init__(self, bot_token: Optional[str] = None):
        """Initialize sender.
        
        Args:
            bot_token: Telegram bot token
        """
        self._bot_token = bot_token
        # TODO: Initialize Telegram bot client

    async def send(self, notification: Notification) -> bool:
        """Send notification via Telegram.
        
        Args:
            notification: Notification to send
            
        Returns:
            True if sent successfully
        """
        try:
            # TODO: Implement actual Telegram sending
            logger.info(
                f"Sending notification {notification.notification_id.value} "
                f"to user {notification.user_id}"
            )

            # Simulate sending
            # In real implementation:
            # await bot.send_message(
            #     chat_id=notification.user_id,
            #     text=f"<b>{notification.title}</b>\n\n{notification.message}",
            #     parse_mode="HTML"
            # )

            return True

        except Exception as e:
            logger.error(
                f"Failed to send notification {notification.notification_id.value}: {e}",
                exc_info=True,
            )
            return False

    async def send_batch(self, notifications: list[Notification]) -> dict[str, bool]:
        """Send multiple notifications.
        
        Args:
            notifications: List of notifications
            
        Returns:
            Dict mapping notification IDs to success status
        """
        results = {}

        for notification in notifications:
            notification_id = notification.notification_id.value
            success = await self.send(notification)
            results[notification_id] = success

        return results

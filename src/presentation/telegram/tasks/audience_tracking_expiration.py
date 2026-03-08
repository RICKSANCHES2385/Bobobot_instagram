"""Audience Tracking Expiration Handler Background Task."""

import asyncio
from datetime import datetime

from aiogram import Bot

from src.domain.audience_tracking.repositories.audience_tracking_repository import (
    AudienceTrackingRepository,
)
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class AudienceTrackingExpirationHandler:
    """Background task for handling expired audience tracking subscriptions."""

    def __init__(
        self,
        bot: Bot,
        tracking_repository: AudienceTrackingRepository,
        check_interval_seconds: int = 3600,  # 1 hour default
    ):
        """Initialize handler.
        
        Args:
            bot: Telegram bot instance
            tracking_repository: Audience tracking repository
            check_interval_seconds: Check interval in seconds
        """
        self.bot = bot
        self.tracking_repository = tracking_repository
        self.check_interval_seconds = check_interval_seconds
        self.is_running = False
        self.task = None

    async def start(self) -> None:
        """Start the handler task."""
        if self.is_running:
            logger.warning("Audience tracking expiration handler is already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self._run())
        logger.info("Audience tracking expiration handler started")

    async def stop(self) -> None:
        """Stop the handler task."""
        if not self.is_running:
            return

        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Audience tracking expiration handler stopped")

    async def _run(self) -> None:
        """Main handler loop."""
        logger.info("Audience tracking expiration handler loop started")
        
        while self.is_running:
            try:
                await self._handle_expired_subscriptions()
                await self._handle_expiring_soon_subscriptions()
            except Exception as e:
                logger.error(f"Error in expiration handler: {e}", exc_info=True)
            
            # Wait for next check
            await asyncio.sleep(self.check_interval_seconds)

    async def _handle_expired_subscriptions(self) -> None:
        """Handle expired subscriptions."""
        logger.info("Checking for expired audience tracking subscriptions")
        
        try:
            expired = await self.tracking_repository.get_expired_subscriptions()
            
            if not expired:
                logger.debug("No expired subscriptions found")
                return
            
            logger.info(f"Found {len(expired)} expired subscriptions")
            
            for tracking in expired:
                try:
                    # Mark as expired
                    tracking.expire()
                    await self.tracking_repository.save(tracking)
                    
                    # Send notification
                    await self._send_expiration_notification(
                        tracking.user_id,
                        tracking.target_username
                    )
                    
                    logger.info(
                        f"Expired tracking {tracking.tracking_id.value} "
                        f"for user {tracking.user_id}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Error expiring tracking {tracking.tracking_id.value}: {e}",
                        exc_info=True
                    )
                    
        except Exception as e:
            logger.error(f"Error handling expired subscriptions: {e}", exc_info=True)

    async def _handle_expiring_soon_subscriptions(self) -> None:
        """Handle subscriptions expiring soon (for auto-renewal)."""
        logger.info("Checking for subscriptions needing renewal")
        
        try:
            for_renewal = await self.tracking_repository.get_subscriptions_for_renewal()
            
            if not for_renewal:
                logger.debug("No subscriptions need renewal")
                return
            
            logger.info(f"Found {len(for_renewal)} subscriptions for renewal")
            
            for tracking in for_renewal:
                try:
                    # Send renewal reminder
                    await self._send_renewal_reminder(
                        tracking.user_id,
                        tracking.target_username,
                        tracking.days_remaining()
                    )
                    
                    logger.info(
                        f"Sent renewal reminder for tracking {tracking.tracking_id.value}"
                    )
                    
                    # TODO: Implement auto-renewal logic
                    # if tracking.auto_renew:
                    #     await self._auto_renew_subscription(tracking)
                    
                except Exception as e:
                    logger.error(
                        f"Error handling renewal for tracking {tracking.tracking_id.value}: {e}",
                        exc_info=True
                    )
                    
        except Exception as e:
            logger.error(f"Error handling renewals: {e}", exc_info=True)

    async def _send_expiration_notification(self, user_id: int, username: str) -> None:
        """Send expiration notification.
        
        Args:
            user_id: User ID
            username: Target username
        """
        try:
            text = (
                f"⏰ <b>Подписка истекла</b>\n\n"
                f"Ваша подписка на Audience Tracking для <b>@{username}</b> истекла.\n\n"
                f"Для продления используйте /instagram @{username}"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent expiration notification to user {user_id}")
            
        except Exception as e:
            logger.error(
                f"Error sending expiration notification to user {user_id}: {e}",
                exc_info=True
            )

    async def _send_renewal_reminder(
        self,
        user_id: int,
        username: str,
        days_remaining: int
    ) -> None:
        """Send renewal reminder.
        
        Args:
            user_id: User ID
            username: Target username
            days_remaining: Days remaining
        """
        try:
            text = (
                f"⏰ <b>Напоминание о продлении</b>\n\n"
                f"Ваша подписка на Audience Tracking для <b>@{username}</b> "
                f"истекает через {days_remaining} дн.\n\n"
                f"Для продления используйте /instagram @{username}"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML"
            )
            
            logger.info(f"Sent renewal reminder to user {user_id}")
            
        except Exception as e:
            logger.error(
                f"Error sending renewal reminder to user {user_id}: {e}",
                exc_info=True
            )

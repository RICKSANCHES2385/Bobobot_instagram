"""Main Telegram bot application with DDD architecture."""

import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.infrastructure.config import Settings, get_settings
from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.handlers import (
    register_command_handlers,
    register_instagram_handlers,
    register_payment_handlers,
    register_tracking_handlers,
)
from src.presentation.telegram.middleware.subscription_check import SubscriptionCheckMiddleware

logger = get_logger(__name__)


class TelegramBot:
    """Telegram bot application."""

    def __init__(self, settings: Settings) -> None:
        """Initialize bot."""
        self.settings = settings
        self.bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        
        # Register middleware
        self._register_middleware()
        
        # Register handlers
        self._register_handlers()

    def _register_middleware(self) -> None:
        """Register middleware."""
        # Subscription check middleware
        # self.dp.message.middleware(SubscriptionCheckMiddleware())
        # self.dp.callback_query.middleware(SubscriptionCheckMiddleware())
        logger.info("Middleware registered")

    def _register_handlers(self) -> None:
        """Register all handlers."""
        register_command_handlers(self.dp)
        register_instagram_handlers(self.dp)
        register_tracking_handlers(self.dp)
        register_payment_handlers(self.dp)
        logger.info("Handlers registered")

    async def start(self) -> None:
        """Start bot polling."""
        logger.info("Starting Telegram bot...")
        logger.info(f"Environment: {self.settings.environment}")
        
        try:
            # Set bot commands
            await self._set_bot_commands()
            
            # Start polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query"],
            )
        except Exception as e:
            logger.exception(f"Error starting bot: {e}")
            raise
        finally:
            await self.bot.session.close()

    async def stop(self) -> None:
        """Stop bot."""
        logger.info("Stopping Telegram bot...")
        await self.dp.stop_polling()
        await self.bot.session.close()

    async def _set_bot_commands(self) -> None:
        """Set bot commands menu."""
        from aiogram.types import BotCommand

        commands = [
            BotCommand(command="start", description="🏠 Перезапустить бота"),
            BotCommand(command="tariffs", description="👑 Тарифы Безлимит"),
            BotCommand(command="sub", description="📊 Мои отслеживания"),
            BotCommand(command="force", description="🔄 Обновления"),
            BotCommand(command="ref", description="👥 Партнёрка"),
            BotCommand(command="support", description="🏛 Поддержка"),
        ]

        try:
            await self.bot.set_my_commands(commands)
            logger.info("Bot commands set successfully")
        except Exception as e:
            logger.warning(f"Failed to set bot commands: {e}")


async def main() -> None:
    """Run bot."""
    settings = get_settings()
    bot = TelegramBot(settings)
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())

"""Telegram handlers."""

from src.presentation.telegram.handlers.command_handlers import register_command_handlers
from src.presentation.telegram.handlers.instagram_handlers import register_instagram_handlers
from src.presentation.telegram.handlers.payment_handlers import register_payment_handlers
from src.presentation.telegram.handlers.tracking_handlers import register_tracking_handlers

__all__ = [
    "register_command_handlers",
    "register_instagram_handlers",
    "register_payment_handlers",
    "register_tracking_handlers",
]

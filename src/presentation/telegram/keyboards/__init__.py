"""Telegram keyboards."""

from src.presentation.telegram.keyboards.instagram_menu import get_profile_keyboard
from src.presentation.telegram.keyboards.main_menu import get_start_keyboard

__all__ = [
    "get_start_keyboard",
    "get_profile_keyboard",
]

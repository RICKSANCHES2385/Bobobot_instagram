"""Tests for TelegramId."""
import pytest
from src.domain.user_management.value_objects.telegram_id import TelegramId


def test_telegram_id_creation():
    """TelegramId should be created with positive int."""
    telegram_id = TelegramId(value=123456789)
    
    assert telegram_id.value == 123456789


def test_telegram_id_validates_positive():
    """TelegramId should validate that value is positive."""
    with pytest.raises(ValueError, match="Telegram ID must be positive"):
        TelegramId(value=0)
    
    with pytest.raises(ValueError, match="Telegram ID must be positive"):
        TelegramId(value=-123)


def test_telegram_id_equality():
    """TelegramIds with same value should be equal."""
    telegram_id1 = TelegramId(value=123456789)
    telegram_id2 = TelegramId(value=123456789)
    telegram_id3 = TelegramId(value=987654321)
    
    assert telegram_id1 == telegram_id2
    assert telegram_id1 != telegram_id3

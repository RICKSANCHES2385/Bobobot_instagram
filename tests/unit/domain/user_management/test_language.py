"""Tests for Language."""
import pytest
from src.domain.user_management.value_objects.language import Language, LanguageCode


def test_language_creation():
    """Language should be created with valid code."""
    language_ru = Language(code=LanguageCode.RU)
    language_en = Language(code=LanguageCode.EN)
    
    assert language_ru.code == LanguageCode.RU
    assert language_en.code == LanguageCode.EN


def test_language_default():
    """Language should have default value (Russian)."""
    language = Language.default()
    
    assert language.code == LanguageCode.RU


def test_language_validates_code():
    """Language should validate code is LanguageCode enum."""
    # Valid codes
    Language(code=LanguageCode.RU)
    Language(code=LanguageCode.EN)
    
    # Invalid code (string instead of enum)
    with pytest.raises(ValueError, match="Invalid language code"):
        Language(code="invalid")  # type: ignore

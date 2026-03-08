"""Language Value Object."""
from dataclasses import dataclass
from enum import Enum
from src.domain.shared.value_objects.base import BaseValueObject


class LanguageCode(str, Enum):
    """Supported language codes."""
    RU = "ru"
    EN = "en"


@dataclass(frozen=True)
class Language(BaseValueObject):
    """User interface language."""
    
    code: LanguageCode
    
    def _validate(self) -> None:
        """Validate language code."""
        if not isinstance(self.code, LanguageCode):
            raise ValueError(f"Invalid language code: {self.code}")
    
    @classmethod
    def default(cls) -> 'Language':
        """Get default language."""
        return cls(code=LanguageCode.RU)

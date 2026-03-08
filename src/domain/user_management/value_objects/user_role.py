"""User Role Value Object."""

from dataclasses import dataclass
from enum import Enum


class UserRoleEnum(str, Enum):
    """User role enumeration."""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


@dataclass(frozen=True)
class UserRole:
    """User role value object."""

    value: UserRoleEnum

    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.value == UserRoleEnum.ADMIN

    def is_premium(self) -> bool:
        """Check if user is premium."""
        return self.value == UserRoleEnum.PREMIUM

    def is_user(self) -> bool:
        """Check if user is regular user."""
        return self.value == UserRoleEnum.USER

    def has_premium_access(self) -> bool:
        """Check if user has premium access (premium or admin)."""
        return self.value in (UserRoleEnum.PREMIUM, UserRoleEnum.ADMIN)

    def __str__(self) -> str:
        """String representation."""
        return self.value.value

"""User DTOs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserDTO:
    """User data transfer object."""

    user_id: str
    telegram_username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    subscription_status: str
    subscription_expires_at: Optional[datetime]
    is_active: bool
    last_activity_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


@dataclass
class RegisterUserDTO:
    """Register user DTO."""

    user_id: str
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class UpdateUserProfileDTO:
    """Update user profile DTO."""

    user_id: str
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class ActivateSubscriptionDTO:
    """Activate subscription DTO."""

    user_id: str
    expires_at: datetime
    is_trial: bool = False

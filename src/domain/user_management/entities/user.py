"""User Entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.shared.entities.base import AggregateRoot
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.user_management.value_objects.user_role import UserRole, UserRoleEnum
from src.domain.user_management.value_objects.telegram_username import TelegramUsername
from src.domain.user_management.value_objects.subscription_status import (
    SubscriptionStatus,
    SubscriptionStatusEnum,
)
from src.domain.user_management.events.user_events import (
    UserRegisteredEvent,
    UserRoleChangedEvent,
    SubscriptionActivatedEvent,
    SubscriptionExpiredEvent,
    SubscriptionCancelledEvent,
)


@dataclass(eq=False)
class User(AggregateRoot):
    """User aggregate root."""

    user_id: UserId = None
    telegram_username: TelegramUsername = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = None
    subscription_status: SubscriptionStatus = None
    subscription_expires_at: Optional[datetime] = None
    is_active: bool = True
    last_activity_at: Optional[datetime] = None

    @staticmethod
    def register(
        user_id: UserId,
        telegram_username: TelegramUsername,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> "User":
        """Register new user.
        
        Args:
            user_id: User ID
            telegram_username: Telegram username
            first_name: First name
            last_name: Last name
            
        Returns:
            User instance
        """
        user = User(
            id=str(user_id.value),
            user_id=user_id,
            telegram_username=telegram_username,
            first_name=first_name,
            last_name=last_name,
            role=UserRole(UserRoleEnum.USER),
            subscription_status=SubscriptionStatus(SubscriptionStatusEnum.EXPIRED),
            is_active=True,
            last_activity_at=datetime.utcnow(),
        )

        user.add_domain_event(
            UserRegisteredEvent(
                user_id=user_id.value,
                telegram_username=telegram_username.value,
                first_name=first_name,
                last_name=last_name,
            )
        )

        return user

    def update_profile(
        self,
        telegram_username: Optional[TelegramUsername] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> None:
        """Update user profile.
        
        Args:
            telegram_username: New username
            first_name: New first name
            last_name: New last name
        """
        if telegram_username is not None:
            self.telegram_username = telegram_username
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name

        self._touch()

    def change_role(self, new_role: UserRole) -> None:
        """Change user role.
        
        Args:
            new_role: New role
        """
        old_role = self.role
        self.role = new_role
        self._touch()

        self.add_domain_event(
            UserRoleChangedEvent(
                user_id=self.user_id.value,
                old_role=old_role.value.value,
                new_role=new_role.value.value,
            )
        )

    def activate_subscription(
        self,
        expires_at: datetime,
        is_trial: bool = False,
    ) -> None:
        """Activate subscription.
        
        Args:
            expires_at: Expiration date
            is_trial: Whether this is a trial subscription
        """
        status = SubscriptionStatusEnum.TRIAL if is_trial else SubscriptionStatusEnum.ACTIVE
        self.subscription_status = SubscriptionStatus(status)
        self.subscription_expires_at = expires_at
        self._touch()

        self.add_domain_event(
            SubscriptionActivatedEvent(
                user_id=self.user_id.value,
                expires_at=expires_at,
                is_trial=is_trial,
            )
        )

    def expire_subscription(self) -> None:
        """Expire subscription."""
        if self.subscription_status.is_expired():
            return

        self.subscription_status = SubscriptionStatus(SubscriptionStatusEnum.EXPIRED)
        self._touch()

        self.add_domain_event(
            SubscriptionExpiredEvent(
                user_id=self.user_id.value,
            )
        )

    def cancel_subscription(self) -> None:
        """Cancel subscription."""
        if not self.subscription_status.is_active():
            raise ValueError("Cannot cancel inactive subscription")

        self.subscription_status = SubscriptionStatus(SubscriptionStatusEnum.CANCELLED)
        self._touch()

        self.add_domain_event(
            SubscriptionCancelledEvent(
                user_id=self.user_id.value,
            )
        )

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.utcnow()
        self._touch()

    def deactivate(self) -> None:
        """Deactivate user."""
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        """Activate user."""
        self.is_active = True
        self._touch()

    def has_active_subscription(self) -> bool:
        """Check if user has active subscription."""
        if not self.subscription_status.is_active():
            return False

        if self.subscription_expires_at is None:
            return False

        return datetime.utcnow() < self.subscription_expires_at

    def get_full_name(self) -> str:
        """Get full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else "Unknown"

    def __str__(self) -> str:
        """String representation."""
        return f"User {self.user_id} ({self.get_full_name()}) - {self.role}"

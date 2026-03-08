"""Tests for User Entity."""

import pytest
from datetime import datetime, timedelta

from src.domain.user_management.entities.user import User
from src.domain.user_management.value_objects.user_id import UserId
from src.domain.user_management.value_objects.user_role import UserRole, UserRoleEnum
from src.domain.user_management.value_objects.telegram_username import TelegramUsername
from src.domain.user_management.value_objects.subscription_status import SubscriptionStatusEnum
from src.domain.user_management.events.user_events import (
    UserRegisteredEvent,
    UserRoleChangedEvent,
    SubscriptionActivatedEvent,
    SubscriptionExpiredEvent,
)


class TestUser:
    """Test user entity."""

    def test_register_user(self):
        """Test registering new user."""
        # Act
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
            first_name="John",
            last_name="Doe",
        )

        # Assert
        assert user.user_id.value == 123456789
        assert user.telegram_username.value == "test_user"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.role.is_user()
        assert user.subscription_status.is_expired()
        assert user.is_active
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], UserRegisteredEvent)

    def test_update_profile(self):
        """Test updating user profile."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )
        user.clear_domain_events()

        # Act
        user.update_profile(
            telegram_username=TelegramUsername("new_username"),
            first_name="Jane",
            last_name="Smith",
        )

        # Assert
        assert user.telegram_username.value == "new_username"
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"

    def test_change_role(self):
        """Test changing user role."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )
        user.clear_domain_events()

        # Act
        user.change_role(UserRole(UserRoleEnum.PREMIUM))

        # Assert
        assert user.role.is_premium()
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], UserRoleChangedEvent)

    def test_activate_subscription(self):
        """Test activating subscription."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )
        user.clear_domain_events()
        expires_at = datetime.utcnow() + timedelta(days=30)

        # Act
        user.activate_subscription(expires_at=expires_at, is_trial=False)

        # Assert
        assert user.subscription_status.is_active()
        assert user.subscription_expires_at == expires_at
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], SubscriptionActivatedEvent)

    def test_activate_trial_subscription(self):
        """Test activating trial subscription."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )
        user.clear_domain_events()
        expires_at = datetime.utcnow() + timedelta(days=7)

        # Act
        user.activate_subscription(expires_at=expires_at, is_trial=True)

        # Assert
        assert user.subscription_status.is_trial()
        assert user.subscription_expires_at == expires_at

    def test_expire_subscription(self):
        """Test expiring subscription."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )
        expires_at = datetime.utcnow() + timedelta(days=30)
        user.activate_subscription(expires_at=expires_at)
        user.clear_domain_events()

        # Act
        user.expire_subscription()

        # Assert
        assert user.subscription_status.is_expired()
        assert len(user.domain_events) == 1
        assert isinstance(user.domain_events[0], SubscriptionExpiredEvent)

    def test_has_active_subscription(self):
        """Test checking active subscription."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )

        # Act & Assert - no subscription
        assert not user.has_active_subscription()

        # Activate subscription
        expires_at = datetime.utcnow() + timedelta(days=30)
        user.activate_subscription(expires_at=expires_at)
        assert user.has_active_subscription()

        # Expire subscription
        user.expire_subscription()
        assert not user.has_active_subscription()

    def test_get_full_name(self):
        """Test getting full name."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
            first_name="John",
            last_name="Doe",
        )

        # Act & Assert
        assert user.get_full_name() == "John Doe"

        # Test with only first name
        user.last_name = None
        assert user.get_full_name() == "John"

        # Test with no name
        user.first_name = None
        assert user.get_full_name() == "Unknown"

    def test_deactivate_user(self):
        """Test deactivating user."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )

        # Act
        user.deactivate()

        # Assert
        assert not user.is_active

    def test_activate_user(self):
        """Test activating user."""
        # Arrange
        user = User.register(
            user_id=UserId(123456789),
            telegram_username=TelegramUsername("test_user"),
        )
        user.deactivate()

        # Act
        user.activate()

        # Assert
        assert user.is_active



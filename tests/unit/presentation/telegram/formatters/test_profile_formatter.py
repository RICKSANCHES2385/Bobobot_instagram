"""Tests for profile formatter."""

from datetime import datetime, timedelta

from src.presentation.telegram.formatters.profile_formatter import (
    format_number,
    format_profile_text,
    format_tracking_status,
    format_audience_status,
    format_subscription_status,
)


class TestFormatNumber:
    """Tests for format_number function."""

    def test_format_small_number(self):
        """Test formatting small numbers."""
        assert format_number(100) == "100"
        assert format_number(999) == "999"

    def test_format_thousands(self):
        """Test formatting thousands."""
        assert format_number(1000) == "1.0K"
        assert format_number(1500) == "1.5K"
        assert format_number(999999) == "1000.0K"

    def test_format_millions(self):
        """Test formatting millions."""
        assert format_number(1000000) == "1.0M"
        assert format_number(1500000) == "1.5M"
        assert format_number(10000000) == "10.0M"


class TestFormatProfileText:
    """Tests for format_profile_text function."""

    def test_format_basic_profile(self):
        """Test formatting basic profile."""
        text = format_profile_text(
            username="cristiano",
            followers_count=500000000,
            following_count=500,
            posts_count=3500,
        )
        
        assert "@cristiano" in text
        assert "500.0M" in text
        assert "3.5K" in text

    def test_format_profile_with_full_name(self):
        """Test formatting profile with full name."""
        text = format_profile_text(
            username="cristiano",
            full_name="Cristiano Ronaldo",
            followers_count=1000,
        )
        
        assert "Cristiano Ronaldo" in text

    def test_format_profile_with_biography(self):
        """Test formatting profile with biography."""
        text = format_profile_text(
            username="test",
            biography="This is a test biography",
            followers_count=100,
        )
        
        assert "This is a test biography" in text

    def test_format_verified_profile(self):
        """Test formatting verified profile."""
        text = format_profile_text(
            username="cristiano",
            is_verified=True,
            followers_count=100,
        )
        
        assert "✓" in text

    def test_format_private_profile(self):
        """Test formatting private profile."""
        text = format_profile_text(
            username="test",
            is_private=True,
            followers_count=100,
        )
        
        assert "🔒" in text

    def test_format_business_profile(self):
        """Test formatting business profile."""
        text = format_profile_text(
            username="test",
            is_business=True,
            followers_count=100,
        )
        
        assert "💼" in text

    def test_format_profile_with_long_biography(self):
        """Test formatting profile with long biography."""
        long_bio = "A" * 300
        text = format_profile_text(
            username="test",
            biography=long_bio,
            followers_count=100,
        )
        
        assert "..." in text
        assert len(text) < len(long_bio) + 200


class TestFormatTrackingStatus:
    """Tests for format_tracking_status function."""

    def test_format_no_tracking(self):
        """Test formatting when tracking is not active."""
        text = format_tracking_status(is_tracking=False)
        
        assert "не активно" in text

    def test_format_active_tracking(self):
        """Test formatting active tracking."""
        text = format_tracking_status(
            is_tracking=True,
            tracking_types=["stories", "posts"],
            interval_hours=6,
        )
        
        assert "активно" in text
        assert "Stories" in text
        assert "Posts" in text
        assert "6 часов" in text

    def test_format_tracking_with_last_check(self):
        """Test formatting tracking with last check time."""
        last_check = datetime.now() - timedelta(hours=2)
        text = format_tracking_status(
            is_tracking=True,
            last_check=last_check,
        )
        
        assert "2 ч назад" in text


class TestFormatAudienceStatus:
    """Tests for format_audience_status function."""

    def test_format_inactive_audience(self):
        """Test formatting inactive audience tracking."""
        text = format_audience_status(is_active=False)
        
        assert "не активен" in text

    def test_format_active_audience(self):
        """Test formatting active audience tracking."""
        text = format_audience_status(
            is_active=True,
            new_followers=10,
            unfollowers=5,
        )
        
        assert "активен" in text
        assert "+10" in text
        assert "-5" in text


class TestFormatSubscriptionStatus:
    """Tests for format_subscription_status function."""

    def test_format_no_subscription(self):
        """Test formatting when no subscription."""
        text = format_subscription_status(is_active=False)
        
        assert "не активна" in text

    def test_format_trial_subscription(self):
        """Test formatting trial subscription."""
        text = format_subscription_status(is_active=True, is_trial=True)
        
        assert "Пробный период" in text

    def test_format_active_subscription(self):
        """Test formatting active subscription."""
        expires_at = datetime.now() + timedelta(days=30)
        text = format_subscription_status(
            is_active=True,
            plan_name="Безлимит 1 месяц",
            expires_at=expires_at,
        )
        
        assert "Безлимит 1 месяц" in text
        assert "30 дн" in text

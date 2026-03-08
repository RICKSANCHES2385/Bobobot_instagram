"""Tests for content formatter."""

from datetime import datetime, timedelta

from src.presentation.telegram.formatters.content_formatter import (
    format_time_ago,
    format_story_caption,
    format_post_caption,
    format_reel_caption,
    format_highlight_caption,
    format_media_group_caption,
)


class TestFormatTimeAgo:
    """Tests for format_time_ago function."""

    def test_format_just_now(self):
        """Test formatting just now."""
        now = datetime.now()
        assert format_time_ago(now) == "только что"

    def test_format_minutes_ago(self):
        """Test formatting minutes ago."""
        time = datetime.now() - timedelta(minutes=5)
        assert "5 мин назад" in format_time_ago(time)

    def test_format_hours_ago(self):
        """Test formatting hours ago."""
        time = datetime.now() - timedelta(hours=3)
        assert "3 ч назад" in format_time_ago(time)

    def test_format_yesterday(self):
        """Test formatting yesterday."""
        time = datetime.now() - timedelta(days=1)
        assert "вчера" in format_time_ago(time)

    def test_format_days_ago(self):
        """Test formatting days ago."""
        time = datetime.now() - timedelta(days=3)
        assert "3 дн назад" in format_time_ago(time)

    def test_format_weeks_ago(self):
        """Test formatting weeks ago."""
        time = datetime.now() - timedelta(weeks=2)
        assert "нед назад" in format_time_ago(time)

    def test_format_months_ago(self):
        """Test formatting months ago."""
        time = datetime.now() - timedelta(days=60)
        assert "мес назад" in format_time_ago(time)

    def test_format_years_ago(self):
        """Test formatting years ago."""
        time = datetime.now() - timedelta(days=400)
        assert "г назад" in format_time_ago(time)


class TestFormatStoryCaption:
    """Tests for format_story_caption function."""

    def test_format_basic_story(self):
        """Test formatting basic story."""
        caption = format_story_caption(
            username="cristiano",
            story_index=1,
            total_stories=5,
        )
        
        assert "Story 1/5" in caption
        assert "@cristiano" in caption

    def test_format_story_with_time(self):
        """Test formatting story with time."""
        created_at = datetime.now() - timedelta(hours=2)
        caption = format_story_caption(
            username="test",
            story_index=1,
            total_stories=3,
            created_at=created_at,
        )
        
        assert "2 ч назад" in caption

    def test_format_story_with_audio(self):
        """Test formatting story with audio."""
        caption = format_story_caption(
            username="test",
            story_index=1,
            total_stories=1,
            has_audio=True,
        )
        
        assert "🔊" in caption


class TestFormatPostCaption:
    """Tests for format_post_caption function."""

    def test_format_photo_post(self):
        """Test formatting photo post."""
        caption = format_post_caption(
            username="cristiano",
            is_video=False,
        )
        
        assert "Фото" in caption
        assert "@cristiano" in caption

    def test_format_video_post(self):
        """Test formatting video post."""
        caption = format_post_caption(
            username="test",
            is_video=True,
        )
        
        assert "Видео" in caption

    def test_format_album_post(self):
        """Test formatting album post."""
        caption = format_post_caption(
            username="test",
            is_album=True,
        )
        
        assert "Альбом" in caption

    def test_format_post_with_stats(self):
        """Test formatting post with statistics."""
        caption = format_post_caption(
            username="test",
            likes_count=1000,
            comments_count=50,
        )
        
        assert "1000" in caption
        assert "50" in caption

    def test_format_post_with_caption(self):
        """Test formatting post with caption text."""
        caption = format_post_caption(
            username="test",
            caption="This is a test caption",
        )
        
        assert "This is a test caption" in caption

    def test_format_post_with_long_caption(self):
        """Test formatting post with long caption."""
        long_caption = "A" * 400
        caption = format_post_caption(
            username="test",
            caption=long_caption,
        )
        
        assert "..." in caption
        assert len(caption) < len(long_caption)


class TestFormatReelCaption:
    """Tests for format_reel_caption function."""

    def test_format_basic_reel(self):
        """Test formatting basic reel."""
        caption = format_reel_caption(username="cristiano")
        
        assert "Reel" in caption
        assert "@cristiano" in caption

    def test_format_reel_with_stats(self):
        """Test formatting reel with statistics."""
        caption = format_reel_caption(
            username="test",
            views_count=10000,
            likes_count=500,
            comments_count=20,
        )
        
        assert "10000" in caption
        assert "500" in caption
        assert "20" in caption

    def test_format_reel_with_duration(self):
        """Test formatting reel with duration."""
        caption = format_reel_caption(
            username="test",
            duration_seconds=90,
        )
        
        assert "1:30" in caption

    def test_format_reel_with_short_duration(self):
        """Test formatting reel with short duration."""
        caption = format_reel_caption(
            username="test",
            duration_seconds=15,
        )
        
        assert "15s" in caption


class TestFormatHighlightCaption:
    """Tests for format_highlight_caption function."""

    def test_format_highlight(self):
        """Test formatting highlight caption."""
        caption = format_highlight_caption(
            username="cristiano",
            highlight_title="Best Moments",
            story_index=1,
            total_stories=10,
        )
        
        assert "Best Moments" in caption
        assert "Story 1/10" in caption
        assert "@cristiano" in caption


class TestFormatMediaGroupCaption:
    """Tests for format_media_group_caption function."""

    def test_format_media_group(self):
        """Test formatting media group caption."""
        caption = format_media_group_caption(
            username="cristiano",
            media_count=5,
        )
        
        assert "Альбом" in caption
        assert "5" in caption
        assert "@cristiano" in caption

    def test_format_media_group_with_caption(self):
        """Test formatting media group with caption."""
        caption = format_media_group_caption(
            username="test",
            media_count=3,
            caption="Album caption",
        )
        
        assert "Album caption" in caption

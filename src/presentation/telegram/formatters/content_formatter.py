"""Content formatter for Instagram media."""

from datetime import datetime
from typing import Optional


def format_time_ago(timestamp: datetime) -> str:
    """Format timestamp as time ago."""
    now = datetime.now()
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "только что"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} мин назад"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} ч назад"
    elif diff.days == 1:
        return "вчера"
    elif diff.days < 7:
        return f"{diff.days} дн назад"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"{weeks} нед назад"
    elif diff.days < 365:
        months = diff.days // 30
        return f"{months} мес назад"
    else:
        years = diff.days // 365
        return f"{years} г назад"


def format_story_caption(
    username: str,
    story_index: int,
    total_stories: int,
    created_at: Optional[datetime] = None,
    has_audio: bool = False,
) -> str:
    """Format story caption."""
    lines = [f"📖 <b>Story {story_index}/{total_stories}</b>"]
    lines.append(f"👤 @{username}")
    
    if created_at:
        lines.append(f"🕐 {format_time_ago(created_at)}")
    
    if has_audio:
        lines.append("🔊 Со звуком")
    
    return "\n".join(lines)


def format_post_caption(
    username: str,
    caption: Optional[str] = None,
    likes_count: Optional[int] = None,
    comments_count: Optional[int] = None,
    created_at: Optional[datetime] = None,
    is_video: bool = False,
    is_album: bool = False,
) -> str:
    """Format post caption."""
    lines = []
    
    # Media type indicator
    if is_album:
        lines.append("📸 <b>Альбом</b>")
    elif is_video:
        lines.append("🎥 <b>Видео</b>")
    else:
        lines.append("📸 <b>Фото</b>")
    
    lines.append(f"👤 @{username}")
    
    # Statistics
    stats = []
    if likes_count is not None:
        stats.append(f"❤️ {likes_count}")
    if comments_count is not None:
        stats.append(f"💬 {comments_count}")
    if stats:
        lines.append(" • ".join(stats))
    
    # Time
    if created_at:
        lines.append(f"🕐 {format_time_ago(created_at)}")
    
    # Caption
    if caption:
        lines.append("")
        # Truncate long captions
        caption_text = caption[:300] + "..." if len(caption) > 300 else caption
        lines.append(caption_text)
    
    return "\n".join(lines)


def format_reel_caption(
    username: str,
    caption: Optional[str] = None,
    views_count: Optional[int] = None,
    likes_count: Optional[int] = None,
    comments_count: Optional[int] = None,
    created_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
) -> str:
    """Format reel caption."""
    lines = ["🎬 <b>Reel</b>"]
    lines.append(f"👤 @{username}")
    
    # Statistics
    stats = []
    if views_count is not None:
        stats.append(f"👁 {views_count}")
    if likes_count is not None:
        stats.append(f"❤️ {likes_count}")
    if comments_count is not None:
        stats.append(f"💬 {comments_count}")
    if stats:
        lines.append(" • ".join(stats))
    
    # Duration
    if duration_seconds:
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        if minutes > 0:
            lines.append(f"⏱ {minutes}:{seconds:02d}")
        else:
            lines.append(f"⏱ {seconds}s")
    
    # Time
    if created_at:
        lines.append(f"🕐 {format_time_ago(created_at)}")
    
    # Caption
    if caption:
        lines.append("")
        # Truncate long captions
        caption_text = caption[:300] + "..." if len(caption) > 300 else caption
        lines.append(caption_text)
    
    return "\n".join(lines)


def format_highlight_caption(
    username: str,
    highlight_title: str,
    story_index: int,
    total_stories: int,
    created_at: Optional[datetime] = None,
) -> str:
    """Format highlight story caption."""
    lines = [f"⭐ <b>{highlight_title}</b>"]
    lines.append(f"Story {story_index}/{total_stories}")
    lines.append(f"👤 @{username}")
    
    if created_at:
        lines.append(f"🕐 {format_time_ago(created_at)}")
    
    return "\n".join(lines)


def format_media_group_caption(
    username: str,
    media_count: int,
    caption: Optional[str] = None,
) -> str:
    """Format media group (album) caption."""
    lines = [f"📸 <b>Альбом ({media_count} фото/видео)</b>"]
    lines.append(f"👤 @{username}")
    
    if caption:
        lines.append("")
        # Truncate long captions
        caption_text = caption[:200] + "..." if len(caption) > 200 else caption
        lines.append(caption_text)
    
    return "\n".join(lines)

"""List formatter for Instagram data exports."""

from datetime import datetime
from typing import List, Dict, Any, Optional


def format_followers_list(
    followers: List[Dict[str, Any]],
    username: str,
    total_count: int,
) -> str:
    """Format followers list for display."""
    lines = [f"👥 <b>Подписчики @{username}</b>"]
    lines.append(f"Всего: {total_count}")
    lines.append("")
    
    for i, follower in enumerate(followers[:50], 1):
        follower_username = follower.get("username", "unknown")
        full_name = follower.get("full_name", "")
        
        line = f"{i}. @{follower_username}"
        if full_name:
            line += f" ({full_name})"
        
        if follower.get("is_verified"):
            line += " ✓"
        
        lines.append(line)
    
    if total_count > 50:
        lines.append("")
        lines.append(f"... и еще {total_count - 50}")
        lines.append("💡 Используйте кнопку 'Скачать всех' для полного списка")
    
    return "\n".join(lines)


def format_following_list(
    following: List[Dict[str, Any]],
    username: str,
    total_count: int,
) -> str:
    """Format following list for display."""
    lines = [f"👤 <b>Подписки @{username}</b>"]
    lines.append(f"Всего: {total_count}")
    lines.append("")
    
    for i, user in enumerate(following[:50], 1):
        user_username = user.get("username", "unknown")
        full_name = user.get("full_name", "")
        
        line = f"{i}. @{user_username}"
        if full_name:
            line += f" ({full_name})"
        
        if user.get("is_verified"):
            line += " ✓"
        
        lines.append(line)
    
    if total_count > 50:
        lines.append("")
        lines.append(f"... и еще {total_count - 50}")
        lines.append("💡 Используйте кнопку 'Скачать всех' для полного списка")
    
    return "\n".join(lines)


def format_posts_list(
    posts: List[Dict[str, Any]],
    username: str,
) -> str:
    """Format posts list for txt file export."""
    lines = [f"Posts from @{username}"]
    lines.append(f"Total: {len(posts)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    lines.append("")
    
    for i, post in enumerate(posts, 1):
        post_id = post.get("id", "unknown")
        shortcode = post.get("shortcode", "")
        caption = post.get("caption", "")
        likes = post.get("likes_count", 0)
        comments = post.get("comments_count", 0)
        created_at = post.get("created_at")
        
        lines.append(f"Post #{i}")
        lines.append(f"URL: https://instagram.com/p/{shortcode}/")
        lines.append(f"Likes: {likes} | Comments: {comments}")
        
        if created_at:
            if isinstance(created_at, datetime):
                lines.append(f"Date: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                lines.append(f"Date: {created_at}")
        
        if caption:
            # Truncate long captions
            caption_text = caption[:200] + "..." if len(caption) > 200 else caption
            lines.append(f"Caption: {caption_text}")
        
        lines.append("-" * 50)
        lines.append("")
    
    return "\n".join(lines)


def format_reels_list(
    reels: List[Dict[str, Any]],
    username: str,
) -> str:
    """Format reels list for txt file export."""
    lines = [f"Reels from @{username}"]
    lines.append(f"Total: {len(reels)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    lines.append("")
    
    for i, reel in enumerate(reels, 1):
        reel_id = reel.get("id", "unknown")
        shortcode = reel.get("shortcode", "")
        caption = reel.get("caption", "")
        views = reel.get("views_count", 0)
        likes = reel.get("likes_count", 0)
        created_at = reel.get("created_at")
        duration = reel.get("duration_seconds", 0)
        
        lines.append(f"Reel #{i}")
        lines.append(f"URL: https://instagram.com/reel/{shortcode}/")
        lines.append(f"Views: {views} | Likes: {likes}")
        
        if duration:
            minutes = duration // 60
            seconds = duration % 60
            lines.append(f"Duration: {minutes}:{seconds:02d}")
        
        if created_at:
            if isinstance(created_at, datetime):
                lines.append(f"Date: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                lines.append(f"Date: {created_at}")
        
        if caption:
            # Truncate long captions
            caption_text = caption[:200] + "..." if len(caption) > 200 else caption
            lines.append(f"Caption: {caption_text}")
        
        lines.append("-" * 50)
        lines.append("")
    
    return "\n".join(lines)


def format_followers_export(
    followers: List[Dict[str, Any]],
    username: str,
) -> str:
    """Format followers for txt file export."""
    lines = [f"Followers of @{username}"]
    lines.append(f"Total: {len(followers)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    lines.append("")
    
    for i, follower in enumerate(followers, 1):
        follower_username = follower.get("username", "unknown")
        full_name = follower.get("full_name", "")
        is_verified = follower.get("is_verified", False)
        is_private = follower.get("is_private", False)
        
        line = f"{i}. @{follower_username}"
        
        if full_name:
            line += f" - {full_name}"
        
        flags = []
        if is_verified:
            flags.append("Verified")
        if is_private:
            flags.append("Private")
        
        if flags:
            line += f" [{', '.join(flags)}]"
        
        lines.append(line)
    
    return "\n".join(lines)


def format_following_export(
    following: List[Dict[str, Any]],
    username: str,
) -> str:
    """Format following for txt file export."""
    lines = [f"Following by @{username}"]
    lines.append(f"Total: {len(following)}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 50)
    lines.append("")
    
    for i, user in enumerate(following, 1):
        user_username = user.get("username", "unknown")
        full_name = user.get("full_name", "")
        is_verified = user.get("is_verified", False)
        is_private = user.get("is_private", False)
        
        line = f"{i}. @{user_username}"
        
        if full_name:
            line += f" - {full_name}"
        
        flags = []
        if is_verified:
            flags.append("Verified")
        if is_private:
            flags.append("Private")
        
        if flags:
            line += f" [{', '.join(flags)}]"
        
        lines.append(line)
    
    return "\n".join(lines)

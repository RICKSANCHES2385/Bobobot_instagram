"""Profile formatter for Instagram profiles."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def format_number(num: int) -> str:
    """Format number with K/M suffixes."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def format_profile_text(
    username: str,
    full_name: Optional[str] = None,
    biography: Optional[str] = None,
    followers_count: int = 0,
    following_count: int = 0,
    posts_count: int = 0,
    is_private: bool = False,
    is_verified: bool = False,
    is_business: bool = False,
    external_url: Optional[str] = None,
) -> str:
    """Format Instagram profile information."""
    # Header with username
    header = f"👤 <b>@{username}</b>"
    
    if is_verified:
        header += " ✓"
    
    if is_business:
        header += " 💼"
    
    if is_private:
        header += " 🔒"
    
    # Full name
    lines = [header]
    if full_name and full_name != username:
        lines.append(f"<b>{full_name}</b>")
    
    lines.append("")
    
    # Statistics
    lines.append("📊 <b>Статистика:</b>")
    lines.append(f"• Публикаций: {format_number(posts_count)}")
    lines.append(f"• Подписчиков: {format_number(followers_count)}")
    lines.append(f"• Подписок: {format_number(following_count)}")
    lines.append("")
    
    # Biography
    if biography:
        lines.append("📝 <b>Описание:</b>")
        # Truncate long biographies
        bio_text = biography[:200] + "..." if len(biography) > 200 else biography
        lines.append(bio_text)
        lines.append("")
    
    # External URL
    if external_url:
        lines.append(f"🔗 <a href='{external_url}'>Ссылка</a>")
        lines.append("")
    
    return "\n".join(lines)


def format_tracking_status(
    is_tracking: bool,
    tracking_types: Optional[List[str]] = None,
    interval_hours: Optional[int] = None,
    last_check: Optional[datetime] = None,
) -> str:
    """Format tracking status information."""
    if not is_tracking:
        return "🔔 <b>Отслеживание:</b> не активно"
    
    lines = ["🔔 <b>Отслеживание:</b> активно"]
    
    if tracking_types:
        type_names = {
            "stories": "📖 Stories",
            "posts": "📸 Posts",
            "followers": "👥 Followers",
            "following": "👤 Following",
        }
        types_str = ", ".join([type_names.get(t, t) for t in tracking_types])
        lines.append(f"• Типы: {types_str}")
    
    if interval_hours:
        if interval_hours == 1:
            interval_str = "каждый час"
        elif interval_hours < 24:
            interval_str = f"каждые {interval_hours} часов"
        else:
            interval_str = f"каждые {interval_hours // 24} дня"
        lines.append(f"• Интервал: {interval_str}")
    
    if last_check:
        time_ago = datetime.now() - last_check
        if time_ago.seconds < 60:
            time_str = "только что"
        elif time_ago.seconds < 3600:
            time_str = f"{time_ago.seconds // 60} мин назад"
        elif time_ago.seconds < 86400:
            time_str = f"{time_ago.seconds // 3600} ч назад"
        else:
            time_str = f"{time_ago.days} дн назад"
        lines.append(f"• Последняя проверка: {time_str}")
    
    return "\n".join(lines)


def format_audience_status(
    is_active: bool,
    new_followers: int = 0,
    unfollowers: int = 0,
    last_update: Optional[datetime] = None,
) -> str:
    """Format audience tracking status."""
    if not is_active:
        return "📊 <b>Audience Tracking:</b> не активен"
    
    lines = ["📊 <b>Audience Tracking:</b> активен"]
    
    if new_followers > 0:
        lines.append(f"• Новых подписчиков: +{new_followers}")
    
    if unfollowers > 0:
        lines.append(f"• Отписались: -{unfollowers}")
    
    if last_update:
        time_ago = datetime.now() - last_update
        if time_ago.seconds < 60:
            time_str = "только что"
        elif time_ago.seconds < 3600:
            time_str = f"{time_ago.seconds // 60} мин назад"
        else:
            time_str = f"{time_ago.seconds // 3600} ч назад"
        lines.append(f"• Обновлено: {time_str}")
    
    return "\n".join(lines)


def format_subscription_status(
    is_active: bool,
    plan_name: Optional[str] = None,
    expires_at: Optional[datetime] = None,
    is_trial: bool = False,
) -> str:
    """Format subscription status."""
    if not is_active:
        return "— Подписка не активна"
    
    if is_trial:
        return "— Пробный период (3 дня)"
    
    lines = []
    if plan_name:
        lines.append(f"— {plan_name}")
    else:
        lines.append("— Подписка активна")
    
    if expires_at:
        days_left = (expires_at - datetime.now()).days
        if days_left > 0:
            lines.append(f"— Осталось: {days_left} дн")
        else:
            lines.append("— Истекает сегодня")
    
    return "\n".join(lines)

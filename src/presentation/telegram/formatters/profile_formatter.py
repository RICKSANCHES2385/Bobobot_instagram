"""Profile formatter for Instagram profiles."""

from datetime import datetime
from typing import Any, Dict, List, Optional


def format_number(num: int) -> str:
    """Format number with thousands separators (e.g., 650,000,000)."""
    return f"{num:,}".replace(",", ",")


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
    """Format Instagram profile information with expandable blockquote."""
    # Header with full name or username
    display_name = full_name if full_name else username
    header = f"👤 {display_name}"
    
    lines = [header, ""]
    
    # Expandable blockquote with details
    blockquote_lines = ["<blockquote expandable>Нажмите, чтобы развернуть..."]
    
    # Biography
    if biography:
        bio_text = biography[:200] + "..." if len(biography) > 200 else biography
        blockquote_lines.append(f"📋 <b>О себе:</b> {bio_text}")
        blockquote_lines.append("")
    
    # External URL
    if external_url:
        blockquote_lines.append(f"🔗 <b>Ссылки:</b> {external_url}")
        blockquote_lines.append("")
    
    # Statistics
    blockquote_lines.append(f"— {format_number(posts_count)} постов")
    blockquote_lines.append(f"— {format_number(followers_count)} подписчиков")
    blockquote_lines.append(f"— {format_number(following_count)} подписок")
    blockquote_lines.append("")
    
    # Content tracking status (placeholder)
    blockquote_lines.append("• <b>Отслеживание контента:</b>")
    blockquote_lines.append("— Истории: выключено")
    blockquote_lines.append("— Публикации: выключено")
    blockquote_lines.append("")
    
    # Audience tracking status (placeholder)
    blockquote_lines.append("• <b>Отслеживание аудитории:</b>")
    blockquote_lines.append("— Подписчики: доступ не активен")
    blockquote_lines.append("— Подписки: доступ не активен")
    
    blockquote_lines.append("</blockquote>")
    
    lines.extend(blockquote_lines)
    lines.append("")
    
    # Verification badge
    if is_verified:
        lines.append("✅ Верифицирован")
    
    if is_private:
        lines.append("🔒 Закрытый профиль")
    
    if is_business:
        lines.append("💼 Бизнес-аккаунт")
    
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
    """Format subscription status with improved date formatting."""
    from .date_formatter import DateFormatter
    
    if not is_active:
        return "💤 <b>Подписка:</b> не активна"
    
    if is_trial:
        if expires_at:
            formatted_date = DateFormatter.format_datetime(expires_at)
            time_remaining = DateFormatter.format_time_remaining(expires_at)
            return (
                f"🎁 <b>Пробный период</b>\n"
                f"⏰ До: {formatted_date}\n"
                f"📅 Осталось: {time_remaining}"
            )
        return "🎁 <b>Пробный период</b> (3 дня)"
    
    lines = []
    if plan_name:
        lines.append(f"💎 <b>{plan_name}</b>")
    else:
        lines.append("💎 <b>Подписка активна</b>")
    
    if expires_at:
        formatted_date = DateFormatter.format_datetime(expires_at)
        time_remaining = DateFormatter.format_time_remaining(expires_at)
        lines.append(f"⏰ До: {formatted_date}")
        lines.append(f"📅 Осталось: {time_remaining}")
    
    return "\n".join(lines)

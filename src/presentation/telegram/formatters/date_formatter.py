"""Date formatting utilities for Telegram bot."""

from datetime import datetime, timezone, timedelta
from typing import Optional


class DateFormatter:
    """Formatter for dates with timezone support."""
    
    # Moscow timezone (UTC+3)
    MOSCOW_TZ = timezone(timedelta(hours=3))
    
    @staticmethod
    def format_datetime(
        dt: datetime,
        tz: Optional[timezone] = None,
        include_timezone: bool = True,
        include_time: bool = True
    ) -> str:
        """Format datetime with timezone.
        
        Args:
            dt: Datetime to format
            tz: Timezone (default: Moscow UTC+3)
            include_timezone: Include timezone info
            include_time: Include time
            
        Returns:
            Formatted datetime string
            
        Examples:
            "10.03.2026 13:12 (UTC +3, Москва)"
            "10.03.2026"
        """
        if tz is None:
            tz = DateFormatter.MOSCOW_TZ
        
        # Convert to target timezone
        if dt.tzinfo is None:
            # Assume UTC if no timezone
            dt = dt.replace(tzinfo=timezone.utc)
        
        dt_local = dt.astimezone(tz)
        
        # Format date
        if include_time:
            formatted = dt_local.strftime("%d.%m.%Y %H:%M")
        else:
            formatted = dt_local.strftime("%d.%m.%Y")
        
        # Add timezone info
        if include_timezone and include_time:
            tz_offset = int(tz.utcoffset(None).total_seconds() / 3600)
            tz_sign = "+" if tz_offset >= 0 else ""
            formatted += f" (UTC {tz_sign}{tz_offset}, Москва)"
        
        return formatted
    
    @staticmethod
    def format_date(dt: datetime) -> str:
        """Format date only (without time).
        
        Args:
            dt: Datetime to format
            
        Returns:
            Formatted date string (e.g., "10.03.2026")
        """
        return DateFormatter.format_datetime(
            dt,
            include_timezone=False,
            include_time=False
        )
    
    @staticmethod
    def format_time_remaining(dt: datetime) -> str:
        """Format time remaining until datetime.
        
        Args:
            dt: Target datetime
            
        Returns:
            Human-readable time remaining
            
        Examples:
            "5 дней"
            "2 часа 30 минут"
            "истек"
        """
        now = datetime.utcnow()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        now = now.replace(tzinfo=timezone.utc)
        delta = dt - now
        
        if delta.total_seconds() <= 0:
            return "истек"
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        parts = []
        
        if days > 0:
            parts.append(f"{days} {DateFormatter._pluralize_days(days)}")
        
        if hours > 0 and days < 7:  # Show hours only if less than a week
            parts.append(f"{hours} {DateFormatter._pluralize_hours(hours)}")
        
        if minutes > 0 and days == 0 and hours < 24:  # Show minutes only if less than a day
            parts.append(f"{minutes} {DateFormatter._pluralize_minutes(minutes)}")
        
        return " ".join(parts) if parts else "менее минуты"
    
    @staticmethod
    def format_subscription_period(days: int) -> str:
        """Format subscription period.
        
        Args:
            days: Number of days
            
        Returns:
            Human-readable period
            
        Examples:
            "1 месяц"
            "3 месяца"
            "1 год"
        """
        if days == 30:
            return "1 месяц"
        elif days == 90:
            return "3 месяца"
        elif days == 180:
            return "6 месяцев"
        elif days == 365:
            return "1 год"
        else:
            return f"{days} {DateFormatter._pluralize_days(days)}"
    
    @staticmethod
    def _pluralize_days(count: int) -> str:
        """Pluralize 'days' in Russian."""
        if count % 10 == 1 and count % 100 != 11:
            return "день"
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return "дня"
        else:
            return "дней"
    
    @staticmethod
    def _pluralize_hours(count: int) -> str:
        """Pluralize 'hours' in Russian."""
        if count % 10 == 1 and count % 100 != 11:
            return "час"
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return "часа"
        else:
            return "часов"
    
    @staticmethod
    def _pluralize_minutes(count: int) -> str:
        """Pluralize 'minutes' in Russian."""
        if count % 10 == 1 and count % 100 != 11:
            return "минута"
        elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
            return "минуты"
        else:
            return "минут"
    
    @staticmethod
    def format_subscription_status(
        subscription_type: str,
        end_date: datetime,
        is_active: bool = True
    ) -> str:
        """Format subscription status message.
        
        Args:
            subscription_type: Type of subscription
            end_date: End date
            is_active: Whether subscription is active
            
        Returns:
            Formatted status message
        """
        if not is_active:
            return "❌ Подписка неактивна"
        
        formatted_date = DateFormatter.format_datetime(end_date)
        time_remaining = DateFormatter.format_time_remaining(end_date)
        
        type_emoji = {
            "trial": "🎁",
            "premium": "💎",
            "basic": "⭐",
        }.get(subscription_type, "📦")
        
        type_name = {
            "trial": "Пробная",
            "premium": "Премиум",
            "basic": "Базовая",
        }.get(subscription_type, subscription_type.capitalize())
        
        return (
            f"{type_emoji} <b>{type_name} подписка</b>\n"
            f"⏰ Активна до: {formatted_date}\n"
            f"📅 Осталось: {time_remaining}"
        )

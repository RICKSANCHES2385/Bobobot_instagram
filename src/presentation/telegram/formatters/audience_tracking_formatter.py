"""Audience Tracking Formatter."""

from datetime import datetime
from typing import List

from src.application.audience_tracking.dtos import AudienceTrackingDTO, AudienceChangeDTO


class AudienceTrackingFormatter:
    """Formatter for audience tracking data."""

    @staticmethod
    def format_tracking_list(trackings: List[AudienceTrackingDTO]) -> str:
        """Format list of trackings.
        
        Args:
            trackings: List of tracking DTOs
            
        Returns:
            Formatted text
        """
        if not trackings:
            return (
                "📊 <b>Audience Tracking</b>\n\n"
                "У вас нет активных подписок\n\n"
                "💡 Используйте /instagram @username для добавления"
            )

        text = "📊 <b>Мои Audience Trackings</b>\n\n"
        
        active_count = sum(1 for t in trackings if t.is_active and not t.is_expired)
        text += f"Активных: {active_count} из {len(trackings)}\n\n"

        for tracking in trackings:
            text += AudienceTrackingFormatter.format_tracking_item(tracking)
            text += "\n"

        return text

    @staticmethod
    def format_tracking_item(tracking: AudienceTrackingDTO) -> str:
        """Format single tracking item.
        
        Args:
            tracking: Tracking DTO
            
        Returns:
            Formatted text
        """
        status_emoji = "✅" if tracking.is_active and not tracking.is_expired else "❌"
        
        text = f"{status_emoji} <b>@{tracking.target_username}</b>\n"
        
        # Status
        if tracking.is_active and not tracking.is_expired:
            text += f"├ 🟢 Активна\n"
        elif tracking.is_expired:
            text += f"├ 🔴 Истекла\n"
        else:
            text += f"├ ⚪️ Неактивна\n"
        
        # Expiration
        text += f"├ 📅 Истекает: {tracking.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"├ ⏳ Осталось: {tracking.days_remaining} дн.\n"
        
        # Stats
        if tracking.last_follower_count is not None:
            text += f"├ 👥 Подписчиков: {tracking.last_follower_count:,}\n"
        if tracking.last_following_count is not None:
            text += f"├ 👤 Подписок: {tracking.last_following_count:,}\n"
        
        # Last check
        if tracking.last_checked_at:
            time_ago = AudienceTrackingFormatter._format_time_ago(tracking.last_checked_at)
            text += f"├ 🔄 Проверено: {time_ago}\n"
        
        # Auto-renew
        if tracking.auto_renew:
            text += f"├ 🔁 Автопродление: включено\n"
        
        # Payment info
        currency_emoji = {
            "XTR": "⭐",
            "RUB": "₽",
            "USDT": "💵",
            "TON": "💎"
        }
        emoji = currency_emoji.get(tracking.currency, "💰")
        text += f"└ {emoji} Оплачено: {tracking.amount_paid} {tracking.currency}\n"
        
        return text

    @staticmethod
    def format_change_notification(change: AudienceChangeDTO) -> str:
        """Format change notification.
        
        Args:
            change: Change DTO
            
        Returns:
            Formatted text
        """
        if change.change_type == "followers":
            emoji = "👥"
            type_name = "Подписчики"
        else:
            emoji = "👤"
            type_name = "Подписки"
        
        # Determine if increase or decrease
        if change.difference > 0:
            trend_emoji = "📈"
            action = "увеличилось"
            sign = "+"
        else:
            trend_emoji = "📉"
            action = "уменьшилось"
            sign = ""
        
        text = (
            f"{trend_emoji} <b>Изменение аудитории</b>\n\n"
            f"Профиль: <b>@{change.target_username}</b>\n"
            f"{emoji} {type_name} {action}\n\n"
            f"Было: {change.old_count:,}\n"
            f"Стало: {change.new_count:,}\n"
            f"Изменение: {sign}{change.difference:,}\n\n"
            f"🕐 {change.timestamp.strftime('%d.%m.%Y %H:%M')}"
        )
        
        return text

    @staticmethod
    def format_tracking_status(tracking: AudienceTrackingDTO) -> str:
        """Format detailed tracking status.
        
        Args:
            tracking: Tracking DTO
            
        Returns:
            Formatted text
        """
        text = f"📊 <b>Audience Tracking: @{tracking.target_username}</b>\n\n"
        
        # Status section
        text += "<b>📍 Статус</b>\n"
        if tracking.is_active and not tracking.is_expired:
            text += "🟢 Активна\n"
        elif tracking.is_expired:
            text += "🔴 Истекла\n"
        else:
            text += "⚪️ Неактивна\n"
        
        text += f"📅 Истекает: {tracking.expires_at.strftime('%d.%m.%Y %H:%M')}\n"
        text += f"⏳ Осталось: {tracking.days_remaining} дн.\n"
        
        if tracking.auto_renew:
            text += "🔁 Автопродление: включено\n"
        
        text += "\n"
        
        # Stats section
        text += "<b>📊 Статистика</b>\n"
        if tracking.last_follower_count is not None:
            text += f"👥 Подписчиков: {tracking.last_follower_count:,}\n"
        else:
            text += "👥 Подписчиков: еще не проверено\n"
        
        if tracking.last_following_count is not None:
            text += f"👤 Подписок: {tracking.last_following_count:,}\n"
        else:
            text += "👤 Подписок: еще не проверено\n"
        
        if tracking.last_checked_at:
            time_ago = AudienceTrackingFormatter._format_time_ago(tracking.last_checked_at)
            text += f"🔄 Последняя проверка: {time_ago}\n"
        
        text += "\n"
        
        # Payment section
        text += "<b>💰 Оплата</b>\n"
        currency_emoji = {
            "XTR": "⭐",
            "RUB": "₽",
            "USDT": "💵",
            "TON": "💎"
        }
        emoji = currency_emoji.get(tracking.currency, "💰")
        text += f"{emoji} Оплачено: {tracking.amount_paid} {tracking.currency}\n"
        
        if tracking.created_at:
            text += f"📅 Создано: {tracking.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        
        return text

    @staticmethod
    def format_price_info(currency: str, amount: float) -> str:
        """Format price information.
        
        Args:
            currency: Currency code
            amount: Price amount
            
        Returns:
            Formatted text
        """
        currency_emoji = {
            "XTR": "⭐",
            "RUB": "₽",
            "USDT": "💵",
            "TON": "💎"
        }
        
        emoji = currency_emoji.get(currency, "💰")
        
        if currency == "XTR":
            return f"{int(amount)} {emoji}"
        else:
            return f"{amount:.2f} {emoji}"

    @staticmethod
    def _format_time_ago(dt: datetime) -> str:
        """Format time ago.
        
        Args:
            dt: Datetime
            
        Returns:
            Formatted time ago string
        """
        now = datetime.utcnow()
        delta = now - dt
        
        if delta.days > 0:
            return f"{delta.days} дн. назад"
        
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} ч. назад"
        
        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes} мин. назад"
        
        return "только что"

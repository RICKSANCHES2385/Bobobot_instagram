"""Referral formatter for Telegram messages."""

from decimal import Decimal

from src.application.referral.dtos import ReferralStatsDTO, ReferralLinkDTO


class ReferralFormatter:
    """Formatter for referral-related messages."""

    @staticmethod
    def format_referral_program_info() -> str:
        """Format referral program information."""
        return (
            "🎁 <b>Партнерская программа</b>\n\n"
            "Приглашайте друзей и получайте <b>5% от их первого платежа</b>!\n\n"
            "📋 <b>Как это работает:</b>\n"
            "1️⃣ Получите свою реферальную ссылку\n"
            "2️⃣ Поделитесь ей с друзьями\n"
            "3️⃣ Когда друг оплатит подписку, вы получите 5% на баланс\n"
            "4️⃣ Выводите заработанное при достижении 1000₽\n\n"
            "💰 <b>Условия выплат:</b>\n"
            "• Минимальная сумма: 1000₽\n"
            "• Комиссия: 5% от первого платежа\n"
            "• Поддержка валют: RUB, XTR, USDT, TON\n\n"
            "🚀 Начните зарабатывать прямо сейчас!"
        )

    @staticmethod
    def format_referral_link(dto: ReferralLinkDTO) -> str:
        """Format referral link message."""
        return (
            f"🔗 <b>Ваша реферальная ссылка</b>\n\n"
            f"<code>{dto.referral_link}</code>\n\n"
            f"📋 Код: <code>{dto.referral_code}</code>\n\n"
            f"Поделитесь этой ссылкой с друзьями и получайте 5% от их первого платежа!"
        )

    @staticmethod
    def format_referral_stats(dto: ReferralStatsDTO) -> str:
        """Format referral statistics."""
        currency_symbol = ReferralFormatter._get_currency_symbol(dto.currency)
        
        return (
            f"📊 <b>Статистика рефералов</b>\n\n"
            f"👥 Всего рефералов: <b>{dto.total_referrals}</b>\n"
            f"✅ Активных (оплатили): <b>{dto.active_referrals}</b>\n\n"
            f"💰 <b>Финансы:</b>\n"
            f"• Заработано: <b>{dto.total_earned:.2f} {currency_symbol}</b>\n"
            f"• Выплачено: <b>{dto.total_paid_out:.2f} {currency_symbol}</b>\n"
            f"• Доступно: <b>{dto.available_balance:.2f} {currency_symbol}</b>\n\n"
            f"📋 Ваш код: <code>{dto.referral_code}</code>\n"
        )

    @staticmethod
    def format_referral_applied_success(referral_code: str) -> str:
        """Format successful referral application message."""
        return (
            f"✅ <b>Реферальный код применен!</b>\n\n"
            f"Вы использовали код: <code>{referral_code}</code>\n\n"
            f"Ваш реферер получит бонус после вашей первой оплаты. Спасибо за регистрацию!"
        )

    @staticmethod
    def format_payout_requested_success(amount: Decimal, currency: str) -> str:
        """Format successful payout request message."""
        currency_symbol = ReferralFormatter._get_currency_symbol(currency)
        
        return (
            f"✅ <b>Запрос на выплату отправлен!</b>\n\n"
            f"Сумма: <b>{amount:.2f} {currency_symbol}</b>\n\n"
            f"Мы обработаем ваш запрос в течение 1-3 рабочих дней.\n"
            f"Вы получите уведомление, когда выплата будет произведена."
        )

    @staticmethod
    def format_minimum_payout_not_reached(
        current_balance: Decimal,
        minimum_payout: Decimal,
        currency: str,
    ) -> str:
        """Format minimum payout not reached error."""
        currency_symbol = ReferralFormatter._get_currency_symbol(currency)
        
        return (
            f"⚠️ <b>Недостаточно средств для выплаты</b>\n\n"
            f"Текущий баланс: <b>{current_balance:.2f} {currency_symbol}</b>\n"
            f"Минимальная сумма: <b>{minimum_payout:.2f} {currency_symbol}</b>\n\n"
            f"Пригласите больше друзей, чтобы достичь минимальной суммы!"
        )

    @staticmethod
    def format_referral_reward_earned(
        reward_amount: Decimal,
        currency: str,
        referred_username: str,
    ) -> str:
        """Format referral reward earned notification."""
        currency_symbol = ReferralFormatter._get_currency_symbol(currency)
        
        return (
            f"🎉 <b>Вы заработали реферальный бонус!</b>\n\n"
            f"Ваш реферал @{referred_username} оплатил подписку.\n"
            f"Вы получили: <b>{reward_amount:.2f} {currency_symbol}</b>\n\n"
            f"Продолжайте приглашать друзей и зарабатывать!"
        )

    @staticmethod
    def format_error(error_message: str) -> str:
        """Format error message."""
        return f"❌ <b>Ошибка:</b> {error_message}"

    @staticmethod
    def _get_currency_symbol(currency: str) -> str:
        """Get currency symbol."""
        symbols = {
            "RUB": "₽",
            "XTR": "⭐",
            "USDT": "USDT",
            "TON": "TON",
        }
        return symbols.get(currency, currency)

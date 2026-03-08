"""Handler for ReferralRewardEarned event."""

from src.domain.referral.events.referral_events import ReferralRewardEarned
from src.application.notification.use_cases.send_notification import SendNotificationUseCase
from src.application.notification.dtos import CreateNotificationDTO
from src.domain.shared.value_objects.currency import Currency


class ReferralRewardEarnedHandler:
    """Handler for ReferralRewardEarned domain event."""

    def __init__(self, send_notification_use_case: SendNotificationUseCase):
        self._send_notification = send_notification_use_case

    async def handle(self, event: ReferralRewardEarned) -> None:
        """Handle ReferralRewardEarned event.
        
        Sends notification to referrer about earned reward.
        
        Args:
            event: ReferralRewardEarned domain event
        """
        # Format currency symbol
        currency_symbols = {
            "RUB": "₽",
            "XTR": "⭐",
            "USDT": "USDT",
            "TON": "TON",
        }
        currency_symbol = currency_symbols.get(event.currency, event.currency)

        # Create notification message
        message = (
            f"🎉 <b>Вы заработали реферальный бонус!</b>\n\n"
            f"Ваш реферал (ID: {event.referred_user_id}) оплатил подписку.\n"
            f"Вы получили: <b>{event.reward_amount:.2f} {currency_symbol}</b>\n\n"
            f"💰 Продолжайте приглашать друзей и зарабатывать!\n"
            f"Используйте /ref для просмотра статистики."
        )

        # Send notification
        try:
            notification_dto = CreateNotificationDTO(
                user_id=event.referrer_user_id,
                message=message,
                notification_type="referral_reward",
            )
            await self._send_notification.execute(notification_dto)
        except Exception as e:
            # Log error but don't fail the payment flow
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send referral reward notification: {e}")

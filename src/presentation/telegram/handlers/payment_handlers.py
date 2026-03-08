"""Payment handlers for Telegram bot."""

from uuid import UUID
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery, Message

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container

logger = get_logger(__name__)


# Payment method selection

def get_payment_method_keyboard() -> InlineKeyboardMarkup:
    """Get payment method selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Telegram Stars", callback_data="payment_stars")],
        [InlineKeyboardButton(text="💳 Банковская карта", callback_data="payment_robokassa")],
        [InlineKeyboardButton(text="🤖 CryptoBot (TON/USDT)", callback_data="payment_crypto")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
    ])


async def buy_subscription_command_callback(callback: CallbackQuery) -> None:
    """Handle buy subscription from callback."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} opened payment menu")

    text = (
        "💎 <b>Выберите способ оплаты:</b>\n\n"
        "⭐ <b>Telegram Stars</b>\n"
        "Оплата через встроенную систему Telegram\n\n"
        "💳 <b>Банковская карта</b>\n"
        "Оплата через Robokassa (Visa, MasterCard, МИР)\n\n"
        "🤖 <b>CryptoBot</b>\n"
        "Оплата криптовалютой (TON, USDT)"
    )

    keyboard = get_payment_method_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def payment_menu_callback(callback: CallbackQuery) -> None:
    """Handle back to payment menu."""
    await buy_subscription_command_callback(callback)


# Telegram Stars

def get_stars_plans_keyboard() -> InlineKeyboardMarkup:
    """Get Stars subscription plans keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц - 299 ⭐", callback_data="buy_1m")],
        [InlineKeyboardButton(text="3 месяца - 799 ⭐ (скидка 11%)", callback_data="buy_3m")],
        [InlineKeyboardButton(text="6 месяцев - 1499 ⭐ (скидка 17%)", callback_data="buy_6m")],
        [InlineKeyboardButton(text="1 год - 2499 ⭐ (скидка 30%)", callback_data="buy_12m")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_menu")]
    ])


async def payment_stars_callback(callback: CallbackQuery) -> None:
    """Handle Stars payment method selection."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} selected Stars payment")

    text = (
        "⭐ <b>Оплата через Telegram Stars</b>\n\n"
        "Выберите период подписки:\n\n"
        "🔥 <b>Безлимитный доступ:</b>\n"
        "• Просмотр сторис и постов\n"
        "• Скачивание медиа\n"
        "• Отслеживание аккаунтов\n"
        "• Без ограничений по запросам\n\n"
        "💡 1 Star ≈ 2₽"
    )

    keyboard = get_stars_plans_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def handle_buy_callback(callback: CallbackQuery) -> None:
    """Handle buy_{plan_code} callback - create Stars invoice."""
    if not callback.data or not callback.from_user or not callback.message:
        return

    await callback.answer()

    # Parse: buy_{plan_code}
    parts = callback.data.split("_")
    if len(parts) < 2:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    plan_code = parts[1]
    user_id = callback.from_user.id

    logger.info(f"User {user_id} selected plan {plan_code}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    # Plan mapping
    plans = {
        "1m": {"name": "1 месяц", "price": 299, "days": 30},
        "3m": {"name": "3 месяца", "price": 799, "days": 90},
        "6m": {"name": "6 месяцев", "price": 1499, "days": 180},
        "12m": {"name": "1 год", "price": 2499, "days": 365},
    }

    plan = plans.get(plan_code)
    if not plan:
        await callback.answer("❌ Неверный тариф", show_alert=True)
        return

    try:
        # Create payment
        from src.application.payment.dtos import CreatePaymentCommand
        
        command = CreatePaymentCommand(
            user_id=user_id,
            amount=plan['price'],
            currency="XTR",
            method="telegram_stars"
        )
        
        payment = await use_cases.create_payment.execute(command)
        
        # Send invoice
        from aiogram.types import LabeledPrice
        
        prices = [LabeledPrice(label=f"Подписка {plan['name']}", amount=plan['price'])]
        
        # Get bot from callback
        bot = callback.bot
        
        await bot.send_invoice(
            chat_id=user_id,
            title=f"Подписка Безлимит - {plan['name']}",
            description=f"Безлимитный доступ на {plan['days']} дней",
            payload=str(payment.id),  # Payment ID as payload
            provider_token="",  # Empty for Stars
            currency="XTR",  # Stars currency
            prices=prices
        )
        
        await callback.message.answer(
            "✅ Счёт отправлен!\n\n"
            "Нажмите на кнопку оплаты выше"
        )
        
    except Exception as e:
        logger.error(f"Error creating payment for user {user_id}: {e}")
        await callback.message.answer(
            "❌ Не удалось создать счёт\n\n"
            "Попробуйте позже или обратитесь в поддержку"
        )


async def precheckout_callback(query: PreCheckoutQuery) -> None:
    """Handle pre-checkout query for Stars payment."""
    logger.info(f"Pre-checkout query from user {query.from_user.id}")

    # TODO: Validate payment via ValidatePaymentUseCase
    
    await query.answer(ok=True)


async def successful_payment_callback(message: Message) -> None:
    """Handle successful Stars payment."""
    if not message.from_user or not message.successful_payment:
        return

    user_id = message.from_user.id
    payment_info = message.successful_payment

    logger.info(f"Successful payment from user {user_id}: {payment_info.telegram_payment_charge_id}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Get payment ID from payload
        payment_id = UUID(payment_info.invoice_payload)
        
        # Complete payment
        from src.application.payment.dtos import CompletePaymentCommand
        
        command = CompletePaymentCommand(
            payment_id=payment_id,
            transaction_id=payment_info.telegram_payment_charge_id
        )
        
        payment = await use_cases.complete_payment.execute(command)
        
        # Get plan info from metadata
        plan_code = payment.metadata.get("plan_code", "1m")
        days = payment.metadata.get("days", 30)
        
        # Create subscription
        from src.application.subscription.dtos import CreateSubscriptionCommand
        
        sub_command = CreateSubscriptionCommand(
            user_id=user_id,
            subscription_type="premium",
            days=days,
            price=payment.amount
        )
        
        subscription = await use_cases.create_subscription.execute(sub_command)
        
        text = (
            "✅ <b>Оплата успешна!</b>\n\n"
            f"Ваша подписка активирована до {subscription.end_date.strftime('%d.%m.%Y')}\n"
            "Спасибо за покупку! 🎉\n\n"
            "Теперь вам доступны все функции бота:\n"
            "• Просмотр stories и posts\n"
            "• Скачивание медиа\n"
            "• Отслеживание аккаунтов\n"
            "• Без ограничений"
        )

        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error processing successful payment for user {user_id}: {e}")
        await message.answer(
            "⚠️ Оплата получена, но возникла ошибка при активации подписки\n\n"
            "Обратитесь в поддержку: /support"
        )


async def successful_audience_tracking_payment(message: Message, target_username: str, target_user_id: str) -> None:
    """Handle successful Audience Tracking payment.
    
    Args:
        message: Message with successful payment
        target_username: Instagram username to track
        target_user_id: Instagram user ID
    """
    if not message.from_user or not message.successful_payment:
        return

    user_id = message.from_user.id
    payment_info = message.successful_payment

    logger.info(f"Successful audience tracking payment from user {user_id}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Get payment ID from payload
        payment_id = UUID(payment_info.invoice_payload)
        
        # Complete payment
        from src.application.payment.dtos import CompletePaymentCommand
        
        command = CompletePaymentCommand(
            payment_id=payment_id,
            transaction_id=payment_info.telegram_payment_charge_id
        )
        
        payment = await use_cases.complete_payment.execute(command)
        
        # Create audience tracking subscription
        from src.application.audience_tracking.dtos import CreateAudienceTrackingDTO
        
        tracking_dto = CreateAudienceTrackingDTO(
            user_id=user_id,
            target_username=target_username,
            target_user_id=target_user_id,
            currency="XTR",
            payment_id=payment.id,
            duration_days=30
        )
        
        tracking = await use_cases.create_audience_tracking.execute(tracking_dto)
        
        text = (
            "✅ <b>Audience Tracking активирован!</b>\n\n"
            f"Профиль: @{target_username}\n"
            f"Активен до: {tracking.expires_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            "🔔 Вы будете получать уведомления об изменениях:\n"
            "• Новые подписчики\n"
            "• Отписавшиеся\n"
            "• Изменения в подписках\n\n"
            "Спасибо за покупку! 🎉"
        )

        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error processing audience tracking payment for user {user_id}: {e}")
        await message.answer(
            "⚠️ Оплата получена, но возникла ошибка при активации отслеживания\n\n"
            "Обратитесь в поддержку: /support"
        )


# Robokassa

def get_robokassa_plans_keyboard() -> InlineKeyboardMarkup:
    """Get Robokassa subscription plans keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц - 299₽", callback_data="robokassa_buy_1m")],
        [InlineKeyboardButton(text="3 месяца - 799₽ (скидка 11%)", callback_data="robokassa_buy_3m")],
        [InlineKeyboardButton(text="6 месяцев - 1499₽ (скидка 17%)", callback_data="robokassa_buy_6m")],
        [InlineKeyboardButton(text="1 год - 2499₽ (скидка 30%)", callback_data="robokassa_buy_12m")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_menu")]
    ])


async def payment_robokassa_callback(callback: CallbackQuery) -> None:
    """Handle Robokassa payment method selection."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} selected Robokassa payment")

    text = (
        "💳 <b>Оплата банковской картой</b>\n\n"
        "Выберите период подписки:\n\n"
        "🔥 <b>Безлимитный доступ:</b>\n"
        "• Просмотр сторис и постов\n"
        "• Скачивание медиа\n"
        "• Отслеживание аккаунтов\n"
        "• Без ограничений по запросам\n\n"
        "💳 Принимаем: Visa, MasterCard, МИР"
    )

    keyboard = get_robokassa_plans_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def robokassa_buy_callback(callback: CallbackQuery) -> None:
    """Handle robokassa_buy_{plan_code} callback."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: robokassa_buy_{plan_code}
    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    plan_code = parts[2]

    logger.info(f"User {callback.from_user.id} selected Robokassa plan {plan_code}")

    # TODO: Create Robokassa payment link
    # TODO: Call CreatePaymentUseCase

    plans = {
        "1m": {"name": "1 месяц", "price": 299},
        "3m": {"name": "3 месяца", "price": 799},
        "6m": {"name": "6 месяцев", "price": 1499},
        "12m": {"name": "1 год", "price": 2499},
    }

    plan = plans.get(plan_code)
    if not plan:
        await callback.answer("❌ Неверный тариф", show_alert=True)
        return

    text = (
        f"💳 <b>Подписка Безлимит - {plan['name']}</b>\n\n"
        f"💰 Цена: {plan['price']}₽\n\n"
        "Нажмите кнопку ниже для перехода к оплате"
    )

    # TODO: Generate real payment link
    payment_url = f"https://robokassa.example.com/pay?plan={plan_code}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить {plan['price']}₽", url=payment_url)],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_robokassa")]
    ])

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def robokassa_result_callback(callback: CallbackQuery) -> None:
    """Handle Robokassa payment result webhook."""
    # TODO: Verify signature
    # TODO: Process payment via ProcessPaymentUseCase
    pass


async def robokassa_success_callback(callback: CallbackQuery) -> None:
    """Handle successful Robokassa payment."""
    if not callback.from_user:
        return

    logger.info(f"Successful Robokassa payment from user {callback.from_user.id}")

    text = (
        "✅ <b>Оплата успешна!</b>\n\n"
        "Ваша подписка активирована\n"
        "Спасибо за покупку! 🎉"
    )

    await callback.message.answer(text)


async def robokassa_fail_callback(callback: CallbackQuery) -> None:
    """Handle failed Robokassa payment."""
    if not callback.from_user:
        return

    logger.info(f"Failed Robokassa payment from user {callback.from_user.id}")

    text = (
        "❌ <b>Оплата не прошла</b>\n\n"
        "Попробуйте еще раз или выберите другой способ оплаты"
    )

    keyboard = get_payment_method_keyboard()

    await callback.message.answer(text, reply_markup=keyboard)


# CryptoBot

def get_crypto_currency_keyboard() -> InlineKeyboardMarkup:
    """Get cryptocurrency selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 TON", callback_data="crypto_ton")],
        [InlineKeyboardButton(text="💵 USDT (TRC-20)", callback_data="crypto_usdt")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_menu")]
    ])


def get_crypto_plans_keyboard(currency: str) -> InlineKeyboardMarkup:
    """Get crypto plans keyboard."""
    if currency == "ton":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1 месяц - 5 TON", callback_data="crypto_ton_buy_1m")],
            [InlineKeyboardButton(text="3 месяца - 13 TON", callback_data="crypto_ton_buy_3m")],
            [InlineKeyboardButton(text="6 месяцев - 25 TON", callback_data="crypto_ton_buy_6m")],
            [InlineKeyboardButton(text="1 год - 42 TON", callback_data="crypto_ton_buy_12m")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_crypto")]
        ])
    else:  # usdt
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1 месяц - $5", callback_data="crypto_usdt_buy_1m")],
            [InlineKeyboardButton(text="3 месяца - $13", callback_data="crypto_usdt_buy_3m")],
            [InlineKeyboardButton(text="6 месяцев - $25", callback_data="crypto_usdt_buy_6m")],
            [InlineKeyboardButton(text="1 год - $42", callback_data="crypto_usdt_buy_12m")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="payment_crypto")]
        ])


async def payment_crypto_callback(callback: CallbackQuery) -> None:
    """Handle CryptoBot payment method selection."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} selected CryptoBot payment")

    text = (
        "🤖 <b>Оплата через CryptoBot</b>\n\n"
        "Выберите криптовалюту:\n\n"
        "💎 <b>TON</b> - The Open Network\n"
        "💵 <b>USDT</b> - Tether (TRC-20)"
    )

    keyboard = get_crypto_currency_keyboard()

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def crypto_ton_callback(callback: CallbackQuery) -> None:
    """Handle TON currency selection."""
    if not callback.from_user:
        return

    await callback.answer()

    text = (
        "💎 <b>Оплата в TON</b>\n\n"
        "Выберите период подписки:"
    )

    keyboard = get_crypto_plans_keyboard("ton")

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def crypto_usdt_callback(callback: CallbackQuery) -> None:
    """Handle USDT currency selection."""
    if not callback.from_user:
        return

    await callback.answer()

    text = (
        "💵 <b>Оплата в USDT (TRC-20)</b>\n\n"
        "Выберите период подписки:"
    )

    keyboard = get_crypto_plans_keyboard("usdt")

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def crypto_buy_callback(callback: CallbackQuery) -> None:
    """Handle crypto_{currency}_buy_{plan_code} callback."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: crypto_{currency}_buy_{plan_code}
    parts = callback.data.split("_")
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    currency = parts[1]
    plan_code = parts[3]

    logger.info(f"User {callback.from_user.id} selected {currency} plan {plan_code}")

    # TODO: Create CryptoBot invoice
    # TODO: Call CreatePaymentUseCase

    plans_ton = {
        "1m": {"name": "1 месяц", "price": "5 TON"},
        "3m": {"name": "3 месяца", "price": "13 TON"},
        "6m": {"name": "6 месяцев", "price": "25 TON"},
        "12m": {"name": "1 год", "price": "42 TON"},
    }

    plans_usdt = {
        "1m": {"name": "1 месяц", "price": "$5"},
        "3m": {"name": "3 месяца", "price": "$13"},
        "6m": {"name": "6 месяцев", "price": "$25"},
        "12m": {"name": "1 год", "price": "$42"},
    }

    plans = plans_ton if currency == "ton" else plans_usdt
    plan = plans.get(plan_code)

    if not plan:
        await callback.answer("❌ Неверный тариф", show_alert=True)
        return

    text = (
        f"🤖 <b>Подписка Безлимит - {plan['name']}</b>\n\n"
        f"💰 Цена: {plan['price']}\n\n"
        "Нажмите кнопку ниже для создания счета"
    )

    # TODO: Generate real CryptoBot invoice link
    invoice_url = f"https://t.me/CryptoBot?start=invoice_{plan_code}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить {plan['price']}", url=invoice_url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data=f"crypto_check_{currency}_{plan_code}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"crypto_{currency}")]
    ])

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except Exception:
        await callback.message.answer(text, reply_markup=keyboard)


async def crypto_check_payment(callback: CallbackQuery) -> None:
    """Handle crypto payment status check."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer("Проверяю статус оплаты...")

    # Parse: crypto_check_{currency}_{plan_code}
    parts = callback.data.split("_", 3)
    if len(parts) < 4:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    currency = parts[2]
    plan_code = parts[3]

    logger.info(f"Checking crypto payment status for user {callback.from_user.id}")

    # TODO: Check payment status via CryptoBot API
    # TODO: If paid, activate subscription

    await callback.answer("⏳ Оплата еще не получена", show_alert=True)


# Tariffs menu

async def tariffs_menu_callback(callback: CallbackQuery) -> None:
    """Handle tariffs menu callback."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} requested tariffs menu")

    # Redirect to payment method selection
    await buy_subscription_command_callback(callback)


async def select_tariff_callback(callback: CallbackQuery) -> None:
    """Handle tariff selection callback."""
    if not callback.data or not callback.from_user:
        return

    await callback.answer()

    # Parse: select_tariff_{plan_code}
    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("❌ Ошибка данных", show_alert=True)
        return

    plan_code = parts[2]

    logger.info(f"User {callback.from_user.id} selected tariff {plan_code}")

    # Show payment methods for selected plan
    await buy_subscription_command_callback(callback)


# Other callbacks

async def partnership_callback(callback: CallbackQuery) -> None:
    """Handle partnership callback."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} requested partnership info")

    # Delete main menu message
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

    # TODO: Get referral stats via GetReferralStatsUseCase
    # TODO: Generate referral link

    text = (
        "👥 <b>Партнёрская программа</b>\n\n"
        "Зарабатывайте на рекомендациях!\n\n"
        "💰 <b>Условия:</b>\n"
        "• 5% от каждой покупки по вашей ссылке\n"
        "• Выплаты от 1000₽\n"
        "• Пожизненные отчисления\n\n"
        "📊 <b>Ваша статистика:</b>\n"
        "• Рефералов: 0\n"
        "• Заработано: 0.00₽\n\n"
        "🔗 <b>Ваш реферальный код:</b> <code>REF123</code>\n"
        "🔗 <b>Ваша реферальная ссылка:</b>\n<code>https://t.me/bot?start=REF123</code>\n\n"
        "💡 Отправьте ссылку друзьям, и получайте 5% от их первого платежа!"
    )

    await callback.message.answer(text)


async def support_callback(callback: CallbackQuery) -> None:
    """Handle support callback."""
    if not callback.from_user:
        return

    await callback.answer()

    logger.info(f"User {callback.from_user.id} requested support")

    # Delete main menu message
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

    # TODO: Get support contacts from settings

    text = (
        "🏛 <b>Поддержка</b>\n\n"
        "Если у вас возникли вопросы или проблемы:\n\n"
        "📧 Email: support@example.com\n"
        "💬 Telegram: @support\n\n"
        "⏰ Время ответа: до 24 часов\n\n"
        "Перед обращением проверьте:\n"
        "• Активна ли подписка\n"
        "• Открыт ли профиль Instagram\n"
        "• Правильно ли указан username"
    )

    await callback.message.answer(text)


# Background tasks

async def cleanup_expired_payments_task() -> None:
    """Background task to cleanup expired payments."""
    # TODO: Implement periodic cleanup
    # TODO: Call CleanupExpiredPaymentsUseCase
    pass


def register_payment_handlers(dp: Dispatcher) -> None:
    """Register payment handlers."""
    # Main payment callbacks
    dp.callback_query.register(buy_subscription_command_callback, F.data == "buy_subscription")
    dp.callback_query.register(payment_menu_callback, F.data == "payment_menu")
    
    # Stars payment
    dp.callback_query.register(payment_stars_callback, F.data == "payment_stars")
    dp.callback_query.register(handle_buy_callback, F.data.startswith("buy_"))
    dp.pre_checkout_query.register(precheckout_callback)
    dp.message.register(successful_payment_callback, F.successful_payment)
    
    # Robokassa payment
    dp.callback_query.register(payment_robokassa_callback, F.data == "payment_robokassa")
    dp.callback_query.register(robokassa_buy_callback, F.data.startswith("robokassa_buy_"))
    
    # CryptoBot payment
    dp.callback_query.register(payment_crypto_callback, F.data == "payment_crypto")
    dp.callback_query.register(crypto_ton_callback, F.data == "crypto_ton")
    dp.callback_query.register(crypto_usdt_callback, F.data == "crypto_usdt")
    dp.callback_query.register(crypto_buy_callback, F.data.startswith("crypto_ton_buy_"))
    dp.callback_query.register(crypto_buy_callback, F.data.startswith("crypto_usdt_buy_"))
    dp.callback_query.register(crypto_check_payment, F.data.startswith("crypto_check_"))
    
    # Other callbacks
    dp.callback_query.register(tariffs_menu_callback, F.data == "tariffs_menu")
    dp.callback_query.register(select_tariff_callback, F.data.startswith("select_tariff_"))
    dp.callback_query.register(partnership_callback, F.data == "partnership")
    dp.callback_query.register(support_callback, F.data == "support")

    logger.info("Payment handlers registered")

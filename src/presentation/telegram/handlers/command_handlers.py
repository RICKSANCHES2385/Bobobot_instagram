"""Command handlers for Telegram bot."""

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from src.infrastructure.logging.logger import get_logger
from src.presentation.telegram.dependencies import get_container
from src.presentation.telegram.keyboards.main_menu import get_start_keyboard
from src.presentation.telegram.formatters.profile_formatter import format_subscription_status

logger = get_logger(__name__)


async def start_command(message: Message) -> None:
    """Handle /start command with referral support."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    
    logger.info(f"User {user_id} started the bot")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    # Parse referral code from deep link
    referral_code = None
    if message.text and len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        logger.info(f"User {user_id} started with referral code: {referral_code}")

    try:
        # Register or get existing user
        from src.application.user_management.dtos.user_dto import RegisterUserDTO
        
        register_dto = RegisterUserDTO(
            user_id=str(user_id),
            telegram_username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user = await use_cases.register_user.execute(register_dto)
        logger.info(f"User registered/retrieved: {user.user_id}")
        
        # Apply referral code if provided
        if referral_code:
            # TODO: Re-enable when referral use cases are updated
            # try:
            #     from src.application.referral.dtos import ApplyReferralCodeDTO
            #     dto = ApplyReferralCodeDTO(
            #         referred_user_id=user_id,
            #         referral_code=referral_code,
            #     )
            #     await use_cases.apply_referral_code.execute(dto)
            #     logger.info(f"Referral code {referral_code} applied for user {user_id}")
            #     
            #     # Send success message
            #     await message.answer(
            #         "✅ <b>Реферальный код применен!</b>\n\n"
            #         f"Вы использовали код: <code>{referral_code}</code>\n\n"
            #         "Ваш реферер получит бонус после вашей первой оплаты. Спасибо за регистрацию!",
            #         parse_mode="HTML"
            #     )
            # except Exception as e:
            #     logger.warning(f"Failed to apply referral code {referral_code}: {e}")
            #     # Don't show error to user, just log it
            logger.info(f"Referral code {referral_code} provided but feature temporarily disabled")
        
        # Create trial subscription if new user
        # Check if user has any subscription
        # TODO: Re-enable when subscription use cases are updated
        # try:
        #     subscription = await use_cases.get_subscription.execute(user_id)
        #     has_subscription = subscription is not None
        # except Exception:
        #     has_subscription = False
        
        has_subscription = False  # Temporary: always create trial
        
        # Create 7-day trial for new users without subscription
        # TODO: Re-enable when subscription use cases are updated
        # if not has_subscription:
        #     try:
        #         from src.application.subscription.dtos import CreateSubscriptionCommand
        #         
        #         trial_command = CreateSubscriptionCommand(
        #             user_id=user_id,
        #             subscription_type="trial",
        #             days=7,
        #             price=0.0
        #         )
        #         
        #         trial_subscription = await use_cases.create_subscription.execute(trial_command)
        #         
        #         logger.info(f"Created 7-day trial subscription for new user {user_id}")
        #         
        #         # Send welcome message with trial info
        #         await message.answer(
        #             "🎉 <b>Добро пожаловать!</b>\n\n"
        #             "✨ Вам активирован <b>пробный период на 7 дней</b>!\n\n"
        #             "В течение этого времени вам доступны:\n"
        #             "• Просмотр профилей Instagram\n"
        #             "• Просмотр stories и постов\n"
        #             "• Скачивание медиа\n"
        #             "• Базовое отслеживание аккаунтов\n\n"
        #             f"⏰ Пробный период до: {trial_subscription.end_date.strftime('%d.%m.%Y')}\n\n"
        #             "После окончания пробного периода вы можете оформить подписку.",
        #             parse_mode="HTML"
        #         )
        #     except Exception as e:
        #         logger.error(f"Failed to create trial subscription for user {user_id}: {e}")
        #         # Don't block user if trial creation fails

    except Exception as e:
        logger.error(f"Error registering user {user_id}: {e}")
        await message.answer(
            "❌ Произошла ошибка при регистрации. Попробуйте позже."
        )
        return

    # Delete command message
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete /start command: {e}")

    # Show start menu
    await show_start_menu(message)


async def show_start_menu(message: Message) -> None:
    """Show start menu with subscription status."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    
    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Get subscription status
        # TODO: Re-enable when subscription use cases are updated
        # sub_status = await use_cases.check_subscription_status.execute(user_id)
        # sub_info = format_subscription_status(sub_status)
        sub_info = "— Подписка не активна (временно недоступно)"
    except Exception as e:
        logger.error(f"Error getting subscription status for user {user_id}: {e}")
        sub_info = "— Подписка не активна"

    text = (
        "👋 Отправь мне <b>имя пользователя</b> или <b>ссылку на профиль</b> "
        "Instagram, чтобы <u>анонимно</u> получить все его истории или другие медиа.\n\n"
        f"👑 <b>Подписка Безлимит ↓</b>\n{sub_info}"
    )

    keyboard = get_start_keyboard()
    await message.answer(text, reply_markup=keyboard)


async def instagram_command(message: Message) -> None:
    """Handle /instagram @username command."""
    if not message.from_user or not message.text:
        return

    # Parse username from command
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "❌ Укажите username Instagram профиля\n\n"
            "Пример: /instagram cristiano"
        )
        return

    username = parts[1].lstrip("@")
    logger.info(f"User {message.from_user.id} requested Instagram profile: {username}")

    # TODO: Check subscription via CheckSubscriptionStatusUseCase
    # TODO: Check rate limits
    # TODO: Fetch profile via FetchInstagramProfileUseCase
    # TODO: Send profile with send_user_profile

    await message.answer(f"🔍 Получаю информацию о @{username}...")


async def buy_command(message: Message) -> None:
    """Handle /buy command - show payment methods."""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested buy menu")

    # Delete command message
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete /buy command: {e}")

    # TODO: Show payment method selection
    text = (
        "💎 <b>Выберите способ оплаты:</b>\n\n"
        "⭐ Telegram Stars\n"
        "💳 Банковская карта (Robokassa)\n"
        "🤖 @CryptoBot (TON/USDT)"
    )

    await message.answer(text)


async def tariffs_command(message: Message) -> None:
    """Handle /tariffs command."""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested tariffs")

    # TODO: Get subscription plans from database
    text = (
        "👑 <b>Тарифы Безлимит</b>\n\n"
        "Выберите период подписки:\n\n"
        "🔥 <b>Безлимитный доступ:</b>\n"
        "• Просмотр сторис и постов\n"
        "• Скачивание медиа\n"
        "• Отслеживание аккаунтов\n"
        "• Без ограничений по запросам\n\n"
        "💰 <b>Цены в Telegram Stars:</b>\n"
        "• 1 месяц: 299 Stars\n"
        "• 3 месяца: 799 Stars (скидка 11%)\n"
        "• 6 месяцев: 1499 Stars (скидка 17%)\n"
        "• 1 год: 2499 Stars (скидка 30%)\n\n"
        "💡 1 Star ≈ 2₽"
    )

    await message.answer(text)


async def sub_command(message: Message) -> None:
    """Handle /sub command - show trackings with individual cards."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    logger.info(f"User {user_id} requested trackings")

    # Delete command message
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete /sub command: {e}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Get user trackings
        # TODO: Re-enable when tracking use cases are updated
        # trackings = await use_cases.get_user_trackings.execute(user_id)
        trackings = []  # Temporary: empty list
        
        if not trackings:
            text = (
                "📊 <b>Мои отслеживания</b>\n\n"
                "У вас нет отслеживаемых аккаунтов\n\n"
                "💡 Чтобы добавить аккаунт:\n"
                "1. Найдите профиль через /instagram @username\n"
                "2. Нажмите кнопку 📊 Отслеживать\n"
                "3. Выберите что отслеживать (Stories, Posts и т.д.)\n"
                "4. Настройте интервал проверки\n\n"
                "🔔 Вы будете получать уведомления о новом контенте!"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 На главную", callback_data="main_menu")]
            ])
            await message.answer(text, reply_markup=keyboard)
            return
        
        # Send individual card for each tracking
        for tracking in trackings:
            # Build tracking info
            interval_text = {
                1: "1ч",
                6: "6ч",
                12: "12ч",
                24: "24ч"
            }.get(tracking.check_interval_hours, f"{tracking.check_interval_hours}ч")
            
            # Get tracking types
            type_icons = {
                "stories": "📖",
                "posts": "📷",
                "followers": "👥",
                "following": "➕"
            }
            
            tracking_lines = []
            for t_type in tracking.tracking_types:
                type_name = t_type.value
                icon = type_icons.get(type_name, "•")
                type_text = {
                    "stories": "Истории",
                    "posts": "Публикации",
                    "followers": "Подписчики",
                    "following": "Подписки"
                }.get(type_name, type_name)
                tracking_lines.append(f"{icon} {type_text} — {interval_text}")
            
            # Format last check time
            if tracking.last_check_at:
                from datetime import datetime
                now = datetime.utcnow()
                delta = now - tracking.last_check_at
                if delta.seconds < 60:
                    last_check = "только что"
                elif delta.seconds < 3600:
                    last_check = f"{delta.seconds // 60} мин назад"
                elif delta.seconds < 86400:
                    last_check = f"{delta.seconds // 3600} ч назад"
                else:
                    last_check = tracking.last_check_at.strftime("%d.%m %H:%M")
            else:
                last_check = "ещё не проверялось"
            
            card_text = (
                f"<b>Отслеживание @{tracking.instagram_username}</b>\n\n"
                + "\n".join(tracking_lines) + "\n\n"
                f"🕐 Последняя проверка: {last_check}"
            )
            
            # Keyboard for each card
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👤 Карточка профиля",
                        callback_data=f"ig_profile_{tracking.instagram_user_id}_{tracking.instagram_username}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Отписаться",
                        callback_data=f"unsubscribe_{tracking.id}"
                    )
                ]
            ])
            
            await message.answer(card_text, reply_markup=keyboard, parse_mode="HTML")
        
        # Final message with "Check all" button
        final_text = (
            "Вы можете сразу проверить новые истории и публикации всех подписок."
        )
        final_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Проверить обновления всех", callback_data="check_all_trackings")],
            [InlineKeyboardButton(text="🏠 На главную", callback_data="main_menu")]
        ])
        await message.answer(final_text, reply_markup=final_keyboard)
        
    except Exception as e:
        logger.error(f"Error getting trackings for user {user_id}: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении отслеживаний. Попробуйте позже."
        )


async def ref_command(message: Message) -> None:
    """Handle /ref command - show partnership."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    logger.info(f"User {user_id} requested referral info")

    # Delete command message
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete /ref command: {e}")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Generate referral code if doesn't exist
        # TODO: Re-enable when referral use cases are updated
        # from src.application.referral.dtos import GenerateReferralCodeDTO
        # dto = GenerateReferralCodeDTO(user_id=user_id)
        # await use_cases.generate_referral_code.execute(dto)
        # 
        # # Get referral stats
        # stats = await use_cases.get_referral_stats.execute(user_id)
        # 
        # # Get referral link
        # link = await use_cases.get_referral_link.execute(user_id)
        
        # Temporary placeholder
        text = (
            "👥 <b>Партнёрская программа</b>\n\n"
            "Зарабатывайте на рекомендациях!\n\n"
            "💰 <b>Условия:</b>\n"
            "• 5% от каждой покупки по вашей ссылке\n"
            "• Выплаты от 1000₽\n"
            "• Пожизненные отчисления\n\n"
            "⚠️ Функция временно недоступна"
        )
        
        text = (
            "👥 <b>Партнёрская программа</b>\n\n"
            "Зарабатывайте на рекомендациях!\n\n"
            "💰 <b>Условия:</b>\n"
            "• 5% от каждой покупки по вашей ссылке\n"
            "• Выплаты от 1000₽\n"
            "• Пожизненные отчисления\n\n"
            "⚠️ Функция временно недоступна"
        )
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error getting referral info for user {user_id}: {e}")
        text = (
            "👥 <b>Партнёрская программа</b>\n\n"
            "Зарабатывайте на рекомендациях!\n\n"
            "💰 <b>Условия:</b>\n"
            "• 5% от каждой покупки по вашей ссылке\n"
            "• Выплаты от 1000₽\n"
            "• Пожизненные отчисления\n\n"
            "❌ Не удалось загрузить статистику. Попробуйте позже."
        )
        await message.answer(text, parse_mode="HTML")


async def support_command(message: Message) -> None:
    """Handle /support command."""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested support")

    # Delete command message
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete /support command: {e}")

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

    await message.answer(text)


async def force_command(message: Message) -> None:
    """Handle /force command - manually check tracking updates."""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested force check")

    # Delete command message
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete /force command: {e}")

    # TODO: Get user trackings via GetUserTrackingsUseCase
    # TODO: Trigger CheckContentUpdatesUseCase for all trackings
    text = (
        "⚡ <b>Проверка обновлений запущена</b>\n\n"
        "Бот проверит все ваши отслеживания и отправит уведомления, "
        "если найдет новый контент.\n\n"
        "Это может занять несколько минут."
    )

    await message.answer(text)


async def tracking_command(message: Message) -> None:
    """Handle /tracking command - show tracked accounts (legacy)."""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested trackings (legacy)")

    # Redirect to /sub
    await sub_command(message)


async def subscription_command(message: Message) -> None:
    """Handle /subscription command - check subscription status (legacy)."""
    if not message.from_user:
        return

    user_id = message.from_user.id
    logger.info(f"User {user_id} requested subscription status")

    # Get use cases
    container = get_container()
    use_cases = container.get_use_cases()

    try:
        # Get subscription status
        # TODO: Re-enable when subscription use cases are updated
        # sub_status = await use_cases.check_subscription_status.execute(user_id)
        # 
        # if sub_status.is_active:
        #     text = (
        #         "💎 <b>Ваша подписка</b>\n\n"
        #         f"✅ Активна до: {sub_status.expires_at.strftime('%d.%m.%Y')}\n"
        #         f"📦 План: {sub_status.plan_name}\n\n"
        #         "Используйте /sub для просмотра отслеживаний"
        #     )
        # else:
        #     text = (
        #         "💎 <b>Ваша подписка</b>\n\n"
        #         "❌ У вас нет активной подписки\n\n"
        #         "Используйте /buy для покупки подписки"
        #     )
        
        text = (
            "💎 <b>Ваша подписка</b>\n\n"
            "⚠️ Функция временно недоступна"
        )
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error getting subscription for user {user_id}: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении подписки. Попробуйте позже."
        )


async def help_command(message: Message) -> None:
    """Handle /help command."""
    if not message.from_user:
        return

    logger.info(f"User {message.from_user.id} requested help")

    text = (
        "❓ <b>Справка</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Главное меню\n"
        "/instagram @username - Получить профиль\n"
        "/tariffs - Тарифы\n"
        "/sub - Мои отслеживания\n"
        "/force - Проверить обновления\n"
        "/ref - Партнёрка\n"
        "/support - Поддержка\n\n"
        "<b>Возможности:</b>\n"
        "• Информация о профиле\n"
        "• Просмотр stories, posts, reels\n"
        "• Скачивание медиа\n"
        "• Отслеживание обновлений\n"
        "• Список подписчиков/подписок\n\n"
        "<b>Пример:</b>\n"
        "/instagram cristiano"
    )

    await message.answer(text)


# Callback handlers

async def back_to_start_callback(callback: CallbackQuery) -> None:
    """Handle back to start callback."""
    if not callback.message or not callback.from_user:
        return

    await callback.answer()

    # Delete current message
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

    # TODO: Get subscription status
    sub_info = "— Подписка не активна"

    text = (
        "👋 Отправь мне <b>имя пользователя</b> или <b>ссылку на профиль</b> "
        "Instagram, чтобы <u>анонимно</u> получить все его истории или другие медиа.\n\n"
        f"👑 <b>Подписка Безлимит ↓</b>\n{sub_info}"
    )

    keyboard = get_start_keyboard()
    await callback.message.answer(text, reply_markup=keyboard)


async def view_content_callback(callback: CallbackQuery) -> None:
    """Handle view content callback."""
    if not callback.message or not callback.from_user:
        return

    await callback.answer()

    # Delete main menu
    try:
        await callback.message.delete()
    except Exception as e:
        logger.warning(f"Could not delete message: {e}")

    text = (
        "Отправь мне <b>имя пользователя</b> или <b>ссылку на профиль</b> "
        "Instagram, чтобы анонимно получить любой его контент 👀\n\n"
        "Или отправь ссылку на <b>историю, публикацию, reels или highlight</b>, "
        "чтобы сохранить их себе в высоком качестве 📥"
    )

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
        ]
    )

    await callback.message.answer(text, reply_markup=keyboard)


def register_command_handlers(dp: Dispatcher) -> None:
    """Register command handlers."""
    # Commands
    dp.message.register(start_command, CommandStart())
    dp.message.register(instagram_command, Command("instagram"))
    dp.message.register(buy_command, Command("buy"))
    dp.message.register(tariffs_command, Command("tariffs"))
    dp.message.register(sub_command, Command("sub"))
    dp.message.register(ref_command, Command("ref"))
    dp.message.register(support_command, Command("support"))
    dp.message.register(force_command, Command("force"))

    # Legacy commands
    dp.message.register(tracking_command, Command("tracking"))
    dp.message.register(subscription_command, Command("subscription"))
    dp.message.register(help_command, Command("help"))

    # Callbacks
    dp.callback_query.register(back_to_start_callback, F.data == "back_to_start")
    dp.callback_query.register(view_content_callback, F.data == "view_content")

    logger.info("Command handlers registered")

"""Referral handlers for Telegram bot."""

from decimal import Decimal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from src.application.referral.dtos import (
    GenerateReferralCodeDTO,
    ApplyReferralCodeDTO,
)
from src.application.referral.use_cases import (
    GenerateReferralCodeUseCase,
    ApplyReferralCodeUseCase,
    GetReferralStatsUseCase,
    GetReferralLinkUseCase,
    RequestReferralPayoutUseCase,
)
from src.domain.referral.exceptions import (
    ReferralException,
    MinimumPayoutNotReachedError,
)
from src.domain.referral.value_objects.referral_reward import ReferralReward
from src.presentation.telegram.formatters.referral_formatter import ReferralFormatter

router = Router(name="referral")


async def referral_program_handler(
    message: Message,
    generate_referral_code_use_case: GenerateReferralCodeUseCase,
    get_referral_link_use_case: GetReferralLinkUseCase,
) -> None:
    """Handle /referral command - show referral program info."""
    user_id = message.from_user.id

    try:
        # Generate referral code if doesn't exist
        dto = GenerateReferralCodeDTO(user_id=user_id)
        await generate_referral_code_use_case.execute(dto)

        # Get referral link
        link_dto = await get_referral_link_use_case.execute(user_id)

        # Format messages
        info_text = ReferralFormatter.format_referral_program_info()
        link_text = ReferralFormatter.format_referral_link(link_dto)

        # Create keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Моя статистика",
                        callback_data="referral_stats",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💰 Запросить выплату",
                        callback_data="referral_payout",
                    )
                ],
            ]
        )

        await message.answer(
            f"{info_text}\n\n{link_text}",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    except Exception as e:
        error_text = ReferralFormatter.format_error(str(e))
        await message.answer(error_text, parse_mode="HTML")


async def referral_stats_callback(
    callback: CallbackQuery,
    get_referral_stats_use_case: GetReferralStatsUseCase,
) -> None:
    """Handle referral stats callback."""
    user_id = callback.from_user.id

    try:
        # Get stats
        stats_dto = await get_referral_stats_use_case.execute(user_id)

        # Format message
        stats_text = ReferralFormatter.format_referral_stats(stats_dto)

        # Create keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔗 Моя ссылка",
                        callback_data="referral_link",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💰 Запросить выплату",
                        callback_data="referral_payout",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="◀️ Назад",
                        callback_data="referral_back",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            stats_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        await callback.answer()

    except ValueError as e:
        error_text = ReferralFormatter.format_error(str(e))
        await callback.message.edit_text(error_text, parse_mode="HTML")
        await callback.answer()


async def referral_link_callback(
    callback: CallbackQuery,
    get_referral_link_use_case: GetReferralLinkUseCase,
) -> None:
    """Handle referral link callback."""
    user_id = callback.from_user.id

    try:
        # Get referral link
        link_dto = await get_referral_link_use_case.execute(user_id)

        # Format message
        link_text = ReferralFormatter.format_referral_link(link_dto)

        # Create keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Статистика",
                        callback_data="referral_stats",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="◀️ Назад",
                        callback_data="referral_back",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            link_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        await callback.answer()

    except ValueError as e:
        error_text = ReferralFormatter.format_error(str(e))
        await callback.message.edit_text(error_text, parse_mode="HTML")
        await callback.answer()


async def referral_payout_callback(
    callback: CallbackQuery,
    request_referral_payout_use_case: RequestReferralPayoutUseCase,
) -> None:
    """Handle referral payout request callback."""
    user_id = callback.from_user.id

    try:
        # Request payout
        referral = await request_referral_payout_use_case.execute(user_id)

        # Format success message
        success_text = ReferralFormatter.format_payout_requested_success(
            amount=referral.get_available_balance().amount,
            currency=referral.total_earned.currency.value,
        )

        # Create keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Статистика",
                        callback_data="referral_stats",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="◀️ Назад",
                        callback_data="referral_back",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            success_text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        await callback.answer("✅ Запрос отправлен!")

    except MinimumPayoutNotReachedError as e:
        # Get current balance from error message
        error_text = ReferralFormatter.format_minimum_payout_not_reached(
            current_balance=Decimal("0"),  # Will be updated from stats
            minimum_payout=ReferralReward.MINIMUM_PAYOUT_RUB,
            currency="RUB",
        )
        await callback.message.edit_text(error_text, parse_mode="HTML")
        await callback.answer("⚠️ Недостаточно средств", show_alert=True)

    except ValueError as e:
        error_text = ReferralFormatter.format_error(str(e))
        await callback.message.edit_text(error_text, parse_mode="HTML")
        await callback.answer()


async def referral_back_callback(
    callback: CallbackQuery,
    generate_referral_code_use_case: GenerateReferralCodeUseCase,
    get_referral_link_use_case: GetReferralLinkUseCase,
) -> None:
    """Handle back to referral program callback."""
    user_id = callback.from_user.id

    try:
        # Get referral link
        link_dto = await get_referral_link_use_case.execute(user_id)

        # Format messages
        info_text = ReferralFormatter.format_referral_program_info()
        link_text = ReferralFormatter.format_referral_link(link_dto)

        # Create keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Моя статистика",
                        callback_data="referral_stats",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="💰 Запросить выплату",
                        callback_data="referral_payout",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            f"{info_text}\n\n{link_text}",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        await callback.answer()

    except Exception as e:
        error_text = ReferralFormatter.format_error(str(e))
        await callback.message.edit_text(error_text, parse_mode="HTML")
        await callback.answer()


def register_referral_handlers(router: Router) -> None:
    """Register referral handlers."""
    router.message.register(referral_program_handler, Command("referral"))
    router.callback_query.register(
        referral_stats_callback,
        F.data == "referral_stats",
    )
    router.callback_query.register(
        referral_link_callback,
        F.data == "referral_link",
    )
    router.callback_query.register(
        referral_payout_callback,
        F.data == "referral_payout",
    )
    router.callback_query.register(
        referral_back_callback,
        F.data == "referral_back",
    )

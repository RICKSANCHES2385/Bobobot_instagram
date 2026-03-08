"""Referral DTOs."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class GenerateReferralCodeDTO:
    """DTO for generating referral code."""

    user_id: int
    currency: str = "RUB"


@dataclass
class ApplyReferralCodeDTO:
    """DTO for applying referral code."""

    referred_user_id: int
    referral_code: str


@dataclass
class ReferralStatsDTO:
    """DTO for referral statistics."""

    referrer_user_id: int
    referral_code: str
    total_referrals: int
    active_referrals: int
    total_earned: Decimal
    total_paid_out: Decimal
    available_balance: Decimal
    currency: str
    first_referral_at: Optional[datetime] = None
    last_payout_at: Optional[datetime] = None


@dataclass
class ReferralRewardDTO:
    """DTO for referral reward calculation."""

    payment_amount: Decimal
    commission_rate: Decimal
    reward_amount: Decimal
    currency: str


@dataclass
class RequestPayoutDTO:
    """DTO for requesting payout."""

    referrer_user_id: int


@dataclass
class ReferralLinkDTO:
    """DTO for referral link."""

    referral_code: str
    referral_link: str
    bot_username: str

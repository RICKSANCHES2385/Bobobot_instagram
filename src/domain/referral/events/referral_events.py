"""Referral domain events."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.domain.shared.events import DomainEvent


@dataclass(frozen=True)
class ReferralApplied(DomainEvent):
    """Event raised when a referral code is applied by a new user."""

    referrer_user_id: int
    referred_user_id: int
    referral_code: str
    applied_at: datetime


@dataclass(frozen=True)
class ReferralRewardEarned(DomainEvent):
    """Event raised when a referrer earns a reward from their referral's payment."""

    referrer_user_id: int
    referred_user_id: int
    payment_id: int
    reward_amount: Decimal
    currency: str
    earned_at: datetime


@dataclass(frozen=True)
class ReferralPayoutRequested(DomainEvent):
    """Event raised when a referrer requests a payout of their rewards."""

    referrer_user_id: int
    payout_amount: Decimal
    currency: str
    requested_at: datetime

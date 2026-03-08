"""Referral domain events."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from src.domain.shared.events import DomainEvent


@dataclass(frozen=True)
class ReferralApplied(DomainEvent):
    """Event raised when a referral code is applied by a new user."""

    referrer_user_id: int = field(default=0)
    referred_user_id: int = field(default=0)
    referral_code: str = field(default="")
    applied_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReferralRewardEarned(DomainEvent):
    """Event raised when a referrer earns a reward from their referral's payment."""

    referrer_user_id: int = field(default=0)
    referred_user_id: int = field(default=0)
    payment_id: int = field(default=0)
    reward_amount: Decimal = field(default=Decimal("0"))
    currency: str = field(default="RUB")
    earned_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReferralPayoutRequested(DomainEvent):
    """Event raised when a referrer requests a payout of their rewards."""

    referrer_user_id: int = field(default=0)
    payout_amount: Decimal = field(default=Decimal("0"))
    currency: str = field(default="RUB")
    requested_at: datetime = field(default_factory=datetime.utcnow)

"""Referral domain module."""

from .aggregates.referral import Referral
from .value_objects.referral_code import ReferralCode
from .value_objects.commission_rate import CommissionRate
from .value_objects.referral_reward import ReferralReward
from .events.referral_events import (
    ReferralApplied,
    ReferralRewardEarned,
    ReferralPayoutRequested,
)
from .repositories.referral_repository import ReferralRepository

__all__ = [
    "Referral",
    "ReferralCode",
    "CommissionRate",
    "ReferralReward",
    "ReferralApplied",
    "ReferralRewardEarned",
    "ReferralPayoutRequested",
    "ReferralRepository",
]

"""Referral use cases."""

from .generate_referral_code import GenerateReferralCodeUseCase
from .apply_referral_code import ApplyReferralCodeUseCase
from .get_referral_stats import GetReferralStatsUseCase
from .calculate_referral_reward import CalculateReferralRewardUseCase
from .request_referral_payout import RequestReferralPayoutUseCase
from .get_referral_link import GetReferralLinkUseCase

__all__ = [
    "GenerateReferralCodeUseCase",
    "ApplyReferralCodeUseCase",
    "GetReferralStatsUseCase",
    "CalculateReferralRewardUseCase",
    "RequestReferralPayoutUseCase",
    "GetReferralLinkUseCase",
]

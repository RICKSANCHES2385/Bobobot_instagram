"""Referral domain exceptions."""

from src.domain.shared.exceptions import DomainException


class ReferralException(DomainException):
    """Base exception for referral domain."""


class InvalidReferralCodeError(ReferralException):
    """Raised when referral code is invalid."""


class ReferralCodeAlreadyUsedError(ReferralException):
    """Raised when user tries to use referral code again."""


class SelfReferralNotAllowedError(ReferralException):
    """Raised when user tries to use their own referral code."""


class MinimumPayoutNotReachedError(ReferralException):
    """Raised when payout amount is below minimum threshold."""


class InvalidCommissionRateError(ReferralException):
    """Raised when commission rate is invalid."""


class InvalidRewardAmountError(ReferralException):
    """Raised when reward amount is invalid."""

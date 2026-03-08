"""Referral code value object."""

import re
from dataclasses import dataclass

from src.domain.referral.exceptions import InvalidReferralCodeError


@dataclass(frozen=True)
class ReferralCode:
    """Referral code value object.
    
    Business rules:
    - Must be 6-12 characters long
    - Can contain only alphanumeric characters and underscores
    - Case-insensitive (stored in uppercase)
    """

    value: str

    def __post_init__(self) -> None:
        """Validate referral code."""
        if not self.value:
            raise InvalidReferralCodeError("Referral code cannot be empty")

        # Convert to uppercase for consistency
        object.__setattr__(self, "value", self.value.upper())

        if len(self.value) < 6 or len(self.value) > 12:
            raise InvalidReferralCodeError(
                "Referral code must be between 6 and 12 characters"
            )

        if not re.match(r"^[A-Z0-9_]+$", self.value):
            raise InvalidReferralCodeError(
                "Referral code can only contain alphanumeric characters and underscores"
            )

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

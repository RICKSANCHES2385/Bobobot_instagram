"""Tracking ID value object."""

from dataclasses import dataclass

from src.domain.shared.value_objects.identifier import Identifier


@dataclass(frozen=True)
class TrackingId(Identifier):
    """Audience tracking subscription identifier."""

    def __post_init__(self) -> None:
        """Validate tracking ID."""
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("Tracking ID must be a positive integer")

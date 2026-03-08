"""Subscription ID Value Object."""
from dataclasses import dataclass
from src.domain.shared.value_objects.identifier import Identifier


@dataclass(frozen=True)
class SubscriptionId(Identifier[int]):
    """Subscription identifier."""
    pass

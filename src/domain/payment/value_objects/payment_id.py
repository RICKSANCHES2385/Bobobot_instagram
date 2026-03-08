"""Payment ID value object."""
from dataclasses import dataclass

from ...shared.value_objects.identifier import Identifier


@dataclass(frozen=True)
class PaymentId(Identifier):
    """Payment ID value object."""

    pass

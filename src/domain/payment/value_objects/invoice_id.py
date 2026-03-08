"""Invoice ID value object."""
from dataclasses import dataclass

from ...shared.value_objects.identifier import Identifier


@dataclass(frozen=True)
class InvoiceId(Identifier):
    """Invoice ID value object."""

    pass

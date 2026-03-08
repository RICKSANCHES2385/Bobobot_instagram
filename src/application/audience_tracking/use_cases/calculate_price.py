"""Calculate Audience Tracking Price Use Case."""

from dataclasses import dataclass

from src.application.shared.use_case import UseCase
from src.domain.audience_tracking.value_objects.tracking_price import TrackingPrice
from src.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PriceCalculationDTO:
    """DTO for price calculation result."""

    currency: str
    amount: float
    formatted: str


class CalculateAudienceTrackingPriceUseCase(UseCase[str, PriceCalculationDTO]):
    """Use case for calculating audience tracking price."""

    async def execute(self, currency: str) -> PriceCalculationDTO:
        """Execute use case.
        
        Args:
            currency: Currency code (RUB, XTR, USDT, TON)
            
        Returns:
            Price calculation DTO
        """
        logger.info(f"Calculating audience tracking price for {currency}")

        if currency == "XTR":
            price = TrackingPrice.for_stars()
        elif currency == "RUB":
            price = TrackingPrice.for_rubles()
        else:
            # For crypto, use RUB equivalent
            price = TrackingPrice(amount=TrackingPrice.RUB_PRICE, currency=currency)

        return PriceCalculationDTO(
            currency=price.currency,
            amount=float(price.amount),
            formatted=str(price),
        )

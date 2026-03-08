"""Use case for creating CryptoBot invoice."""

from dataclasses import dataclass
from typing import Optional

from ....domain.payment.value_objects.currency import Currency
from ....infrastructure.payment.adapters.cryptobot_adapter import (
    CryptoBotAdapter,
    CryptoBotInvoice
)
from ....infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CreateCryptoBotInvoiceRequest:
    """Request for creating CryptoBot invoice."""
    
    user_id: int
    plan_code: str
    currency: Currency
    amount: float
    description: str
    expires_in: int = 3600  # 1 hour


@dataclass
class CreateCryptoBotInvoiceResponse:
    """Response for creating CryptoBot invoice."""
    
    success: bool
    invoice_id: Optional[int] = None
    pay_url: Optional[str] = None
    amount: Optional[str] = None
    asset: Optional[str] = None
    error_message: Optional[str] = None


class CreateCryptoBotInvoiceUseCase:
    """Use case for creating CryptoBot invoice."""
    
    def __init__(self, cryptobot_adapter: CryptoBotAdapter):
        """Initialize use case."""
        self.cryptobot_adapter = cryptobot_adapter
    
    async def execute(
        self,
        request: CreateCryptoBotInvoiceRequest
    ) -> CreateCryptoBotInvoiceResponse:
        """Execute use case."""
        try:
            # Create payload for tracking
            payload = (
                f"user_{request.user_id}_"
                f"plan_{request.plan_code}_"
                f"{request.currency.value.lower()}"
            )
            
            # Create invoice via CryptoBot
            invoice = await self.cryptobot_adapter.create_invoice(
                currency=request.currency,
                amount=request.amount,
                description=request.description,
                payload=payload,
                expires_in=request.expires_in
            )
            
            if invoice:
                logger.info(
                    f"Created CryptoBot invoice {invoice.invoice_id} "
                    f"for user {request.user_id}"
                )
                
                return CreateCryptoBotInvoiceResponse(
                    success=True,
                    invoice_id=invoice.invoice_id,
                    pay_url=invoice.pay_url,
                    amount=invoice.amount,
                    asset=invoice.asset
                )
            
            return CreateCryptoBotInvoiceResponse(
                success=False,
                error_message="Failed to create invoice"
            )
            
        except Exception as e:
            logger.error(f"Error creating CryptoBot invoice: {e}")
            return CreateCryptoBotInvoiceResponse(
                success=False,
                error_message=str(e)
            )

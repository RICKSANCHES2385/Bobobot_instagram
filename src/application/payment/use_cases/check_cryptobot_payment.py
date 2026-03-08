"""Use case for checking CryptoBot payment status."""

from dataclasses import dataclass
from typing import Optional

from ....infrastructure.payment.adapters.cryptobot_adapter import CryptoBotAdapter
from ....infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CheckCryptoBotPaymentRequest:
    """Request for checking CryptoBot payment."""
    
    invoice_id: int


@dataclass
class CheckCryptoBotPaymentResponse:
    """Response for checking CryptoBot payment."""
    
    success: bool
    status: Optional[str] = None  # active, paid, expired
    paid: bool = False
    amount: Optional[str] = None
    asset: Optional[str] = None
    payload: Optional[str] = None
    error_message: Optional[str] = None


class CheckCryptoBotPaymentUseCase:
    """Use case for checking CryptoBot payment status."""
    
    def __init__(self, cryptobot_adapter: CryptoBotAdapter):
        """Initialize use case."""
        self.cryptobot_adapter = cryptobot_adapter
    
    async def execute(
        self,
        request: CheckCryptoBotPaymentRequest
    ) -> CheckCryptoBotPaymentResponse:
        """Execute use case."""
        try:
            # Get invoice by ID
            invoice = await self.cryptobot_adapter.get_invoice_by_id(
                request.invoice_id
            )
            
            if not invoice:
                return CheckCryptoBotPaymentResponse(
                    success=False,
                    error_message="Invoice not found"
                )
            
            is_paid = invoice.status == "paid"
            
            logger.info(
                f"Checked CryptoBot invoice {request.invoice_id}: "
                f"status={invoice.status}"
            )
            
            return CheckCryptoBotPaymentResponse(
                success=True,
                status=invoice.status,
                paid=is_paid,
                amount=invoice.amount,
                asset=invoice.asset,
                payload=invoice.payload
            )
            
        except Exception as e:
            logger.error(f"Error checking CryptoBot payment: {e}")
            return CheckCryptoBotPaymentResponse(
                success=False,
                error_message=str(e)
            )

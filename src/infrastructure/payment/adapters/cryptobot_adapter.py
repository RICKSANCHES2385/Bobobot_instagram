"""CryptoBot payment adapter for cryptocurrency payments."""

from datetime import datetime
from typing import Optional, List
import httpx

from ....domain.payment.value_objects.currency import Currency, CurrencyEnum
from ....domain.payment.value_objects.payment_method import PaymentMethod
from ....infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class CryptoBotInvoice:
    """CryptoBot invoice model."""
    
    def __init__(
        self,
        invoice_id: int,
        status: str,
        hash: str,
        currency_type: str,
        asset: str,
        amount: str,
        pay_url: str,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        paid_at: Optional[datetime] = None,
        payload: Optional[str] = None
    ):
        self.invoice_id = invoice_id
        self.status = status
        self.hash = hash
        self.currency_type = currency_type
        self.asset = asset
        self.amount = amount
        self.pay_url = pay_url
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.paid_at = paid_at
        self.payload = payload


class CryptoBotAdapter:
    """Adapter for @CryptoBot API integration."""
    
    def __init__(self, api_token: str):
        """Initialize CryptoBot adapter."""
        self.api_token = api_token
        self.base_url = "https://pay.crypt.bot/api"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.headers = {
            "Crypto-Pay-API-Token": self.api_token,
            "Content-Type": "application/json"
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def get_me(self) -> dict:
        """Get information about the current app."""
        try:
            response = await self.client.get(
                f"{self.base_url}/getMe",
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                return data["result"]
            
            logger.error(f"CryptoBot API error: {data}")
            return {}
                
        except Exception as e:
            logger.error(f"Error getting CryptoBot info: {e}")
            return {}
    
    async def get_currencies(self) -> List[dict]:
        """Get list of supported currencies."""
        try:
            response = await self.client.get(
                f"{self.base_url}/getCurrencies",
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("ok"):
                return data["result"]
            
            logger.error(f"CryptoBot API error: {data}")
            return []
                
        except Exception as e:
            logger.error(f"Error getting currencies: {e}")
            return []
    
    async def create_invoice(
        self,
        currency: Currency,
        amount: float,
        description: str = "",
        payload: str = "",
        expires_in: int = 3600
    ) -> Optional[CryptoBotInvoice]:
        """Create invoice for payment."""
        try:
            # Map Currency to CryptoBot asset
            asset = self._map_currency_to_asset(currency)
            if not asset:
                logger.error(f"Unsupported currency for CryptoBot: {currency.value}")
                return None
            
            data = {
                "asset": asset,
                "amount": str(amount),
                "description": description,
                "payload": payload,
                "expires_in": expires_in
            }
            
            response = await self.client.post(
                f"{self.base_url}/createInvoice",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                invoice_data = result["result"]
                
                invoice = CryptoBotInvoice(
                    invoice_id=invoice_data["invoice_id"],
                    status=invoice_data["status"],
                    hash=invoice_data["hash"],
                    currency_type=invoice_data["currency_type"],
                    asset=invoice_data["asset"],
                    amount=invoice_data["amount"],
                    pay_url=invoice_data["pay_url"],
                    description=invoice_data.get("description"),
                    created_at=datetime.fromisoformat(
                        invoice_data["created_at"].replace("Z", "+00:00")
                    ),
                    payload=invoice_data.get("payload")
                )
                
                logger.info(
                    f"Created CryptoBot invoice {invoice.invoice_id} "
                    f"for {amount} {asset}"
                )
                return invoice
            
            logger.error(f"CryptoBot create invoice error: {result}")
            return None
                
        except Exception as e:
            logger.error(f"Error creating CryptoBot invoice: {e}")
            return None
    
    async def get_invoice_by_id(
        self,
        invoice_id: int
    ) -> Optional[CryptoBotInvoice]:
        """Get specific invoice by ID."""
        invoices = await self.get_invoices(invoice_ids=[invoice_id])
        return invoices[0] if invoices else None
    
    async def get_invoices(
        self,
        asset: Optional[str] = None,
        invoice_ids: Optional[List[int]] = None,
        status: Optional[str] = None,
        offset: int = 0,
        count: int = 100
    ) -> List[CryptoBotInvoice]:
        """Get list of invoices."""
        try:
            params = {
                "offset": offset,
                "count": count
            }
            
            if asset:
                params["asset"] = asset
            if invoice_ids:
                params["invoice_ids"] = ",".join(map(str, invoice_ids))
            if status:
                params["status"] = status
            
            response = await self.client.get(
                f"{self.base_url}/getInvoices",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                invoices = []
                for invoice_data in result["result"]["items"]:
                    invoice = CryptoBotInvoice(
                        invoice_id=invoice_data["invoice_id"],
                        status=invoice_data["status"],
                        hash=invoice_data["hash"],
                        currency_type=invoice_data["currency_type"],
                        asset=invoice_data["asset"],
                        amount=invoice_data["amount"],
                        pay_url=invoice_data["pay_url"],
                        description=invoice_data.get("description"),
                        created_at=datetime.fromisoformat(
                            invoice_data["created_at"].replace("Z", "+00:00")
                        ),
                        paid_at=datetime.fromisoformat(
                            invoice_data["paid_at"].replace("Z", "+00:00")
                        ) if invoice_data.get("paid_at") else None,
                        payload=invoice_data.get("payload")
                    )
                    invoices.append(invoice)
                
                return invoices
            
            logger.error(f"CryptoBot get invoices error: {result}")
            return []
                
        except Exception as e:
            logger.error(f"Error getting invoices: {e}")
            return []
    
    async def check_invoice_status(
        self,
        invoice_id: int
    ) -> Optional[str]:
        """Check invoice payment status."""
        invoice = await self.get_invoice_by_id(invoice_id)
        return invoice.status if invoice else None
    
    def _map_currency_to_asset(self, currency: Currency) -> Optional[str]:
        """Map Currency value object to CryptoBot asset."""
        mapping = {
            CurrencyEnum.TON: "TON",
            CurrencyEnum.USDT: "USDT"
        }
        return mapping.get(currency.value)

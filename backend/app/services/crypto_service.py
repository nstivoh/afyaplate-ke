"""
Coinbase Commerce — crypto payment service.
Supports BTC, ETH, USDC, and other major cryptocurrencies.

Docs: https://docs.cdp.coinbase.com/commerce-onchain/docs/getting-started
"""
import os
import logging
import hashlib
import hmac
import httpx

logger = logging.getLogger(__name__)

COINBASE_BASE = "https://api.commerce.coinbase.com"


class CryptoService:
    def __init__(self):
        self.api_key = os.getenv("COINBASE_COMMERCE_API_KEY", "")
        self.webhook_secret = os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET", "")

    async def create_charge(
        self,
        amount_usd: float,
        user_token: str,
        redirect_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Creates a Coinbase Commerce charge and returns the hosted payment URL.
        Customer chooses their crypto currency on the Coinbase-hosted page.
        """
        if not self.api_key:
            raise Exception("COINBASE_COMMERCE_API_KEY not configured.")

        payload = {
            "name": "AfyaPlate KE Pro",
            "description": "Monthly Pro subscription",
            "pricing_type": "fixed_price",
            "local_price": {"amount": str(amount_usd), "currency": "USD"},
            "metadata": {"user_token": user_token},
            "redirect_url": redirect_url,
            "cancel_url": cancel_url,
        }

        headers = {
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(
                    f"{COINBASE_BASE}/charges",
                    headers=headers,
                    json=payload,
                )
                logger.info(f"Coinbase Commerce response: {resp.status_code}")
                if resp.status_code not in (200, 201):
                    logger.error(f"Coinbase Commerce error: {resp.text}")
                    raise Exception(f"Coinbase Commerce returned HTTP {resp.status_code}")
                data = resp.json()["data"]
                return {
                    "payment_url": data["hosted_url"],
                    "charge_id": data["id"],
                    "charge_code": data["code"],
                }
            except httpx.TimeoutException:
                raise Exception("Coinbase Commerce request timed out.")
            except Exception as e:
                logger.error(f"Coinbase Commerce charge creation failed: {e}")
                raise

    def verify_webhook_signature(self, raw_body: bytes, signature: str) -> bool:
        """Verify Coinbase Commerce webhook HMAC-SHA256 signature."""
        if not self.webhook_secret:
            return False
        expected = hmac.new(
            self.webhook_secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


crypto_service = CryptoService()

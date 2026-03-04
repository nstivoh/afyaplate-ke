"""
Flutterwave payment service — card payments via hosted payment link.
Supports Visa/Mastercard + KE mobile money in one integration.

Docs: https://developer.flutterwave.com/docs/collecting-payments/standard
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

FLW_BASE = "https://api.flutterwave.com/v3"


class FlutterwaveService:
    def __init__(self):
        self.secret_key = os.getenv("FLUTTERWAVE_SECRET_KEY", "")
        self.public_key = os.getenv("FLUTTERWAVE_PUBLIC_KEY", "")

    async def create_payment_link(
        self,
        amount: int,
        currency: str,
        user_token: str,
        email: str,
        redirect_url: str,
    ) -> dict:
        """
        Creates a hosted Flutterwave payment link and returns the URL
        to redirect the customer to for card/mobile payment.
        """
        if not self.secret_key:
            raise Exception("FLUTTERWAVE_SECRET_KEY not configured.")

        payload = {
            "tx_ref": f"afyaplate-{user_token[:8]}",
            "amount": amount,
            "currency": currency,
            "redirect_url": redirect_url,
            "meta": {"user_token": user_token},
            "customer": {
                "email": email,
                "name": "AfyaPlate Customer",
            },
            "customizations": {
                "title": "AfyaPlate KE Pro",
                "description": "Monthly Pro subscription — KES 500",
                "logo": "https://afyaplateke.com/logo.png",
            },
        }

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(f"{FLW_BASE}/payments", headers=headers, json=payload)
                logger.info(f"Flutterwave response: {resp.status_code}")
                if resp.status_code != 200:
                    logger.error(f"Flutterwave error: {resp.text}")
                    raise Exception(f"Flutterwave returned HTTP {resp.status_code}")
                data = resp.json()
                return {
                    "payment_url": data["data"]["link"],
                    "tx_ref": payload["tx_ref"],
                }
            except httpx.TimeoutException:
                raise Exception("Flutterwave request timed out.")
            except Exception as e:
                logger.error(f"Flutterwave payment link creation failed: {e}")
                raise

    async def verify_transaction(self, transaction_id: str) -> dict:
        """Verify a completed Flutterwave transaction by ID."""
        if not self.secret_key:
            raise Exception("FLUTTERWAVE_SECRET_KEY not configured.")
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{FLW_BASE}/transactions/{transaction_id}/verify",
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()


flutterwave_service = FlutterwaveService()

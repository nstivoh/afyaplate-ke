import os
import base64
import json
import logging
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        self.consumer_key = os.getenv("MPESA_CONSUMER_KEY", "0GUqGdwEpwWmVGMoMfN51LafFQQhXy7batFbTtvUlk2DKWo5")
        self.consumer_secret = os.getenv("MPESA_CONSUMER_SECRET", "8rPhSvk3Idjd5UdAE5ceZQ4iKraCIhRPIFN2d0JN14dt5wdO2U53QqjtvRWOnWH8")
        self.shortcode = os.getenv("MPESA_SHORTCODE", "174379")
        self.passkey = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
        self.base_url = "https://sandbox.safaricom.co.ke"

    async def get_access_token(self) -> str:
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        credentials = f"{self.consumer_key}:{self.consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("access_token")
            except Exception as e:
                logger.error(f"Failed to get M-Pesa access token: {e}")
                raise Exception(f"Failed to get access token: {str(e)}")

    async def trigger_stk_push(self, phone_number: str, amount: int) -> dict:
        """
        Trigger an M-Pesa STK push.
        """
        # Ensure phone number is formatted correctly (starts with 254)
        clean_phone = "".join(filter(str.isdigit, phone_number))
        if clean_phone.startswith("0"):
            clean_phone = "254" + clean_phone[1:]
        elif not clean_phone.startswith("254"):
            clean_phone = "254" + clean_phone
            
        access_token = await self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # NOTE: A real public URL is strictly required for production.
        # Sandbox accepts any valid URL format even if unreachable.
        callback_url = os.getenv("MPESA_CALLBACK_URL", "https://mydomain.com/api/v1/payments/mpesa-callback")
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": clean_phone,
            "PartyB": self.shortcode,
            "PhoneNumber": clean_phone,
            "CallBackURL": callback_url,
            "AccountReference": "AfyaPlate KE",
            "TransactionDesc": "Meal Plan Premium"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"M-Pesa API Error: {e.response.text}")
                try:
                    error_data = e.response.json()
                    raise Exception(f"M-Pesa Error: {error_data.get('errorMessage', str(e))}")
                except Exception:
                    raise Exception(f"M-Pesa HTTP Error: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Failed to trigger STK push: {e}")
                raise Exception(f"M-Pesa Request Failed: {str(e)}")

mpesa_service = MpesaService()

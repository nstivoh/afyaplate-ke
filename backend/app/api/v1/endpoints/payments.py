# backend/app/api/v1/endpoints/payments.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mpesa_service import mpesa_service
from app.services.flutterwave_service import flutterwave_service
from app.services.crypto_service import crypto_service

router = APIRouter()

class PaymentRequest(BaseModel):
    phone_number: str
    amount: int

class CardCheckoutRequest(BaseModel):
    amount: int
    currency: str = "KES"
    email: str
    user_token: str
    redirect_url: str

class CryptoCheckoutRequest(BaseModel):
    amount_usd: float
    user_token: str
    redirect_url: str
    cancel_url: str

# ── M-Pesa ────────────────────────────────────────────────────────────────────

@router.post("/stk-push")
async def stk_push_endpoint(request: PaymentRequest):
    """Trigger an M-Pesa STK Push."""
    try:
        response = await mpesa_service.trigger_stk_push(
            phone_number=request.phone_number,
            amount=request.amount
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mpesa-callback")
async def mpesa_callback_endpoint(data: dict):
    """Receive M-Pesa payment callback from Safaricom."""
    print("--- M-PESA CALLBACK RECEIVED ---")
    print(data)
    print("--------------------------------")
    # TODO: Extract user_token from AccountReference or metadata,
    # then call subscription.upgrade() to activate Pro
    return {"status": "success"}

# ── Card (Flutterwave) ────────────────────────────────────────────────────────

@router.post("/card-checkout")
async def card_checkout_endpoint(request: CardCheckoutRequest):
    """Create a Flutterwave hosted payment link for card/mobile payments."""
    try:
        result = await flutterwave_service.create_payment_link(
            amount=request.amount,
            currency=request.currency,
            user_token=request.user_token,
            email=request.email,
            redirect_url=request.redirect_url,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/card-callback")
async def card_callback_endpoint(status: str = "", tx_ref: str = "", transaction_id: str = ""):
    """
    Flutterwave redirects here after payment.
    Verify the transaction, then upgrade the subscription.
    """
    if status == "successful" and transaction_id:
        try:
            await flutterwave_service.verify_transaction(transaction_id)
            # TODO: Extract user_token from tx_ref and call subscription upgrade
        except Exception:
            pass
    return {"status": status, "tx_ref": tx_ref}

# ── Crypto (Coinbase Commerce) ────────────────────────────────────────────────

@router.post("/crypto-checkout")
async def crypto_checkout_endpoint(request: CryptoCheckoutRequest):
    """Create a Coinbase Commerce charge for crypto payment."""
    try:
        result = await crypto_service.create_charge(
            amount_usd=request.amount_usd,
            user_token=request.user_token,
            redirect_url=request.redirect_url,
            cancel_url=request.cancel_url,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crypto-webhook")
async def crypto_webhook_endpoint(request_body: bytes, x_cc_webhook_signature: str = ""):
    """
    Coinbase Commerce webhook — fires when a payment is confirmed on-chain.
    Verifies HMAC signature and upgrades the subscription.
    """
    if not crypto_service.verify_webhook_signature(request_body, x_cc_webhook_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")
    # TODO: Parse event, check payment status, extract user_token, upgrade subscription
    return {"status": "received"}

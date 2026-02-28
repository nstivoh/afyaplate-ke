# backend/app/api/v1/endpoints/payments.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mpesa_service import mpesa_service

router = APIRouter()

class PaymentRequest(BaseModel):
    phone_number: str
    amount: int

@router.post("/stk-push")
async def stk_push_endpoint(request: PaymentRequest):
    """
    Endpoint to trigger an M-Pesa STK Push.
    """
    try:
        response = await mpesa_service.trigger_stk_push(
            phone_number=request.phone_number,
            amount=request.amount
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder for the callback URL that M-Pesa will call
@router.post("/mpesa-callback")
async def mpesa_callback_endpoint(data: dict):
    """
    Placeholder endpoint for receiving M-Pesa callbacks.
    In a real app, this is where you'd get the final transaction status.
    """
    print("--- M-PESA CALLBACK RECEIVED ---")
    print(data)
    print("--------------------------------")
    # Here you would process the callback, check the status,
    # and update the user's subscription status in the database.
    return {"status": "success"}

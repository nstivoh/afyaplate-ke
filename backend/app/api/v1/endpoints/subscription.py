# backend/app/api/v1/endpoints/subscription.py
"""
Subscription management endpoints:
  GET  /subscription/status         — get current plan for a device token
  POST /subscription/start-trial    — begin 14-day free trial
  POST /subscription/upgrade        — mark subscription as Pro after payment
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.subscription import SQLSubscription
from app.dependencies.subscription import get_or_create_subscription

router = APIRouter()
logger = logging.getLogger(__name__)

TRIAL_DAYS = 14
PRO_DURATION_DAYS = 30


# ── Response Schemas ──────────────────────────────────────────────────────────

class SubscriptionStatus(BaseModel):
    plan: str
    is_active: bool
    trial_days_left: int
    expires_at: str | None

    class Config:
        from_attributes = True


class UpgradeRequest(BaseModel):
    payment_method: str   # 'mpesa' | 'card' | 'crypto'
    payment_ref: str      # transaction ID / reference from payment provider


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_status(sub: SQLSubscription) -> SubscriptionStatus:
    return SubscriptionStatus(
        plan=sub.plan,
        is_active=sub.is_active_pro,
        trial_days_left=sub.trial_days_left,
        expires_at=sub.expires_at.isoformat() if sub.expires_at else None,
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/status", response_model=SubscriptionStatus)
def get_status(
    x_user_token: str = Header(None),
    db: Session = Depends(get_db),
):
    """Return the current subscription status for a device token."""
    if not x_user_token:
        return SubscriptionStatus(plan="free", is_active=False, trial_days_left=0, expires_at=None)
    sub = get_or_create_subscription(x_user_token, db)
    return _to_status(sub)


@router.post("/start-trial", response_model=SubscriptionStatus)
def start_trial(
    x_user_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """Start a 14-day free trial. Only allowed once per device token."""
    if not x_user_token:
        raise HTTPException(400, "User token required")

    sub = get_or_create_subscription(x_user_token, db)

    if sub.plan in ("trial", "pro"):
        raise HTTPException(400, "Trial already used or already a Pro subscriber.")

    sub.plan = "trial"
    sub.trial_start = datetime.utcnow()
    sub.expires_at = datetime.utcnow() + timedelta(days=TRIAL_DAYS)
    db.commit()
    db.refresh(sub)
    logger.info(f"Trial started for token {x_user_token[:8]}... expires {sub.expires_at}")
    return _to_status(sub)


@router.post("/upgrade", response_model=SubscriptionStatus)
def upgrade_to_pro(
    body: UpgradeRequest,
    x_user_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Mark a subscription as Pro after successful payment verification.
    In production you would verify the payment_ref with the provider before upgrading.
    """
    if not x_user_token:
        raise HTTPException(400, "User token required")

    sub = get_or_create_subscription(x_user_token, db)

    sub.plan = "pro"
    # Extend from now or from existing expiry (for renewals)
    base = max(datetime.utcnow(), sub.expires_at or datetime.utcnow())
    sub.expires_at = base + timedelta(days=PRO_DURATION_DAYS)
    db.commit()
    db.refresh(sub)
    logger.info(
        f"Upgraded to Pro via {body.payment_method} (ref={body.payment_ref}) "
        f"token={x_user_token[:8]}... expires={sub.expires_at}"
    )
    return _to_status(sub)

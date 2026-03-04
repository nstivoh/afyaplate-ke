"""
FastAPI dependency that enforces Pro or Trial subscription.
Apply with: sub=Depends(require_pro) on any protected endpoint.
"""
import logging
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.models.subscription import SQLSubscription

logger = logging.getLogger(__name__)

PLAN_LIMITS = {
    "free": {
        "algorithmic_plans_per_month": 3,
        "clients": 3,
        "ai_planner": False,
        "pdf_export": False,
    },
    "trial": {
        "algorithmic_plans_per_month": None,  # unlimited
        "clients": 25,
        "ai_planner": True,
        "pdf_export": True,
    },
    "pro": {
        "algorithmic_plans_per_month": None,  # unlimited
        "clients": None,  # unlimited
        "ai_planner": True,
        "pdf_export": True,
    },
}


def get_or_create_subscription(user_token: str, db: Session) -> SQLSubscription:
    """Fetch the subscription for a token, creating a free one if it doesn't exist."""
    sub = db.query(SQLSubscription).filter(SQLSubscription.user_token == user_token).first()
    if not sub:
        sub = SQLSubscription(user_token=user_token, plan="free")
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


async def get_subscription(
    x_user_token: str = Header(None),
    db: Session = Depends(get_db),
) -> SQLSubscription:
    """
    Soft dependency — returns subscription for any token.
    Returns a free-tier subscription if no token is provided.
    """
    if not x_user_token:
        # Return an in-memory free subscription for anonymous visitors
        return SQLSubscription(user_token="anonymous", plan="free")
    return get_or_create_subscription(x_user_token, db)


async def require_pro(
    x_user_token: str = Header(None),
    db: Session = Depends(get_db),
) -> SQLSubscription:
    """
    Hard dependency — raises 403 if user is not on Pro/Trial or trial has expired.
    Apply to Pro-only endpoints.
    """
    if not x_user_token:
        raise HTTPException(
            status_code=403,
            detail="Pro subscription required. Start a free 14-day trial at AfyaPlate KE.",
        )
    sub = get_or_create_subscription(x_user_token, db)
    if not sub.is_active_pro:
        raise HTTPException(
            status_code=403,
            detail=(
                "Your trial has expired. Upgrade to AfyaPlate Pro to continue."
                if sub.plan == "trial"
                else "Pro subscription required. Start a free 14-day trial."
            ),
        )
    return sub

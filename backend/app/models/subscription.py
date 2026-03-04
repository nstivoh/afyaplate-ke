from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.database import Base


class SQLSubscription(Base):
    """
    Stores subscription state per anonymous device token.
    plan: 'free' | 'trial' | 'pro'
    """
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_token = Column(String, unique=True, index=True, nullable=False)
    plan = Column(String, default="free", nullable=False)
    trial_start = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def is_active_pro(self) -> bool:
        if self.plan == "free":
            return False
        if self.expires_at is None:
            return False
        return self.expires_at > datetime.utcnow()

    @property
    def trial_days_left(self) -> int:
        if self.plan != "trial" or self.expires_at is None:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

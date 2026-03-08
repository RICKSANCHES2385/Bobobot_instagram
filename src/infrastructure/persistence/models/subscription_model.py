"""SQLAlchemy model for Subscription aggregate."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from ..base import Base
import enum


class SubscriptionStatusEnum(str, enum.Enum):
    """Subscription status enum for database."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SubscriptionTypeEnum(str, enum.Enum):
    """Subscription type enum for database."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class SubscriptionModel(Base):
    """SQLAlchemy model for subscriptions."""
    
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(20), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(SQLEnum(SubscriptionTypeEnum), nullable=False)
    status = Column(SQLEnum(SubscriptionStatusEnum), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    price_amount = Column(Numeric(10, 2), nullable=False)
    price_currency = Column(String(3), nullable=False)
    auto_renew = Column(Integer, nullable=False, default=0)  # 0=False, 1=True
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="subscriptions")
    
    def __repr__(self) -> str:
        return f"<SubscriptionModel(id={self.id}, user_id={self.user_id}, type={self.type}, status={self.status})>"

"""Referral SQLAlchemy model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from src.infrastructure.persistence.database import Base


class ReferralModel(Base):
    """Referral model for database persistence."""

    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_user_id = Column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One referral code per user
    )
    referral_code = Column(String(12), nullable=False, unique=True, index=True)
    commission_rate = Column(Numeric(5, 4), nullable=False, default=Decimal("0.05"))
    
    # Earnings tracking
    total_earned_amount = Column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    total_paid_out_amount = Column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    currency = Column(String(10), nullable=False, default="RUB")
    
    # Referral tracking
    referred_user_id = Column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,  # User can only be referred once
    )
    applied_at = Column(DateTime, nullable=True)
    first_payment_at = Column(DateTime, nullable=True)
    last_payout_at = Column(DateTime, nullable=True)
    referral_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    referrer = relationship(
        "UserModel",
        foreign_keys=[referrer_user_id],
        back_populates="referral",
    )
    referred_user = relationship(
        "UserModel",
        foreign_keys=[referred_user_id],
        back_populates="referred_by",
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_referrals_referrer_user_id", "referrer_user_id"),
        Index("ix_referrals_referred_user_id", "referred_user_id"),
        Index("ix_referrals_referral_code", "referral_code"),
    )

    def __repr__(self) -> str:
        return (
            f"<ReferralModel(id={self.id}, "
            f"referrer_user_id={self.referrer_user_id}, "
            f"referral_code={self.referral_code}, "
            f"referral_count={self.referral_count})>"
        )

"""SQLAlchemy implementation of ReferralRepository."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.referral.aggregates.referral import Referral
from src.domain.referral.repositories.referral_repository import ReferralRepository
from src.domain.referral.value_objects.commission_rate import CommissionRate
from src.domain.referral.value_objects.referral_code import ReferralCode
from src.domain.referral.value_objects.referral_reward import ReferralReward
from src.domain.shared.value_objects.currency import Currency
from src.infrastructure.persistence.models.referral_model import ReferralModel


class SqlAlchemyReferralRepository(ReferralRepository):
    """SQLAlchemy implementation of ReferralRepository."""

    def __init__(self, session: AsyncSession):
        """Initialize repository.
        
        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, referral: Referral) -> Referral:
        """Save or update a referral."""
        # Check if referral exists
        if hasattr(referral, "id") and referral.id:
            # Update existing
            stmt = select(ReferralModel).where(ReferralModel.id == referral.id)
            result = await self._session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                self._update_model_from_aggregate(model, referral)
            else:
                model = self._aggregate_to_model(referral)
                self._session.add(model)
        else:
            # Create new
            model = self._aggregate_to_model(referral)
            self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_aggregate(model)

    async def find_by_id(self, referral_id: int) -> Optional[Referral]:
        """Find referral by ID."""
        stmt = select(ReferralModel).where(ReferralModel.id == referral_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_aggregate(model) if model else None

    async def find_by_referrer_user_id(
        self, referrer_user_id: int
    ) -> Optional[Referral]:
        """Find referral by referrer user ID."""
        stmt = select(ReferralModel).where(
            ReferralModel.referrer_user_id == referrer_user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_aggregate(model) if model else None

    async def find_by_referral_code(
        self, referral_code: ReferralCode
    ) -> Optional[Referral]:
        """Find referral by referral code."""
        stmt = select(ReferralModel).where(
            ReferralModel.referral_code == str(referral_code)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_aggregate(model) if model else None

    async def find_by_referred_user_id(
        self, referred_user_id: int
    ) -> Optional[Referral]:
        """Find referral by referred user ID."""
        stmt = select(ReferralModel).where(
            ReferralModel.referred_user_id == referred_user_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        return self._model_to_aggregate(model) if model else None

    async def get_referral_stats(self, referrer_user_id: int) -> dict:
        """Get referral statistics for a user."""
        # Get referral
        referral = await self.find_by_referrer_user_id(referrer_user_id)
        if not referral:
            return {
                "total_referrals": 0,
                "active_referrals": 0,
                "total_earned": Decimal("0"),
                "total_paid_out": Decimal("0"),
                "available_balance": Decimal("0"),
            }

        # Count active referrals (those who made payments)
        stmt = select(func.count(ReferralModel.id)).where(
            ReferralModel.referrer_user_id == referrer_user_id,
            ReferralModel.first_payment_at.isnot(None),
        )
        result = await self._session.execute(stmt)
        active_referrals = result.scalar() or 0

        available_balance = referral.get_available_balance()

        return {
            "total_referrals": referral.referral_count,
            "active_referrals": active_referrals,
            "total_earned": referral.total_earned.amount,
            "total_paid_out": referral.total_paid_out.amount,
            "available_balance": available_balance.amount,
        }

    async def exists_by_referral_code(self, referral_code: ReferralCode) -> bool:
        """Check if referral code already exists."""
        stmt = select(func.count(ReferralModel.id)).where(
            ReferralModel.referral_code == str(referral_code)
        )
        result = await self._session.execute(stmt)
        count = result.scalar()
        return count > 0

    async def delete(self, referral_id: int) -> None:
        """Delete a referral."""
        stmt = select(ReferralModel).where(ReferralModel.id == referral_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()

    def _aggregate_to_model(self, referral: Referral) -> ReferralModel:
        """Convert aggregate to model."""
        model = ReferralModel(
            referrer_user_id=referral.referrer_user_id,
            referral_code=str(referral.referral_code),
            commission_rate=referral.commission_rate.rate,
            total_earned_amount=referral.total_earned.amount,
            total_paid_out_amount=referral.total_paid_out.amount,
            currency=referral.total_earned.currency.value,
            referred_user_id=referral.referred_user_id,
            applied_at=referral.applied_at,
            first_payment_at=referral.first_payment_at,
            last_payout_at=referral.last_payout_at,
            referral_count=referral.referral_count,
        )

        if hasattr(referral, "id") and referral.id:
            model.id = referral.id

        return model

    def _update_model_from_aggregate(
        self, model: ReferralModel, referral: Referral
    ) -> None:
        """Update model from aggregate."""
        model.referrer_user_id = referral.referrer_user_id
        model.referral_code = str(referral.referral_code)
        model.commission_rate = referral.commission_rate.rate
        model.total_earned_amount = referral.total_earned.amount
        model.total_paid_out_amount = referral.total_paid_out.amount
        model.currency = referral.total_earned.currency.value
        model.referred_user_id = referral.referred_user_id
        model.applied_at = referral.applied_at
        model.first_payment_at = referral.first_payment_at
        model.last_payout_at = referral.last_payout_at
        model.referral_count = referral.referral_count

    def _model_to_aggregate(self, model: ReferralModel) -> Referral:
        """Convert model to aggregate."""
        referral = Referral(
            referrer_user_id=model.referrer_user_id,
            referral_code=ReferralCode(model.referral_code),
            commission_rate=CommissionRate(rate=model.commission_rate),
            total_earned=ReferralReward(
                amount=model.total_earned_amount,
                currency=Currency(model.currency),
            ),
            total_paid_out=ReferralReward(
                amount=model.total_paid_out_amount,
                currency=Currency(model.currency),
            ),
            referred_user_id=model.referred_user_id,
            applied_at=model.applied_at,
            first_payment_at=model.first_payment_at,
            last_payout_at=model.last_payout_at,
            referral_count=model.referral_count,
        )

        # Set ID
        object.__setattr__(referral, "id", model.id)

        return referral

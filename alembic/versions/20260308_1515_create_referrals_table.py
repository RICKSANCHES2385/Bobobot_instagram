"""Create referrals table

Revision ID: 20260308_1515
Revises: 20260308_1436
Create Date: 2026-03-08 15:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create referrals table."""
    op.create_table(
        'referrals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('referrer_user_id', sa.BigInteger(), nullable=False),
        sa.Column('referral_code', sa.String(length=12), nullable=False),
        sa.Column('commission_rate', sa.Numeric(precision=5, scale=4), nullable=False, server_default='0.0500'),
        sa.Column('total_earned_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_paid_out_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='RUB'),
        sa.Column('referred_user_id', sa.BigInteger(), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('first_payment_at', sa.DateTime(), nullable=True),
        sa.Column('last_payout_at', sa.DateTime(), nullable=True),
        sa.Column('referral_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['referrer_user_id'], ['users.telegram_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['referred_user_id'], ['users.telegram_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referrer_user_id'),
        sa.UniqueConstraint('referral_code'),
        sa.UniqueConstraint('referred_user_id'),
    )
    
    # Create indexes for performance
    op.create_index('ix_referrals_referrer_user_id', 'referrals', ['referrer_user_id'])
    op.create_index('ix_referrals_referred_user_id', 'referrals', ['referred_user_id'])
    op.create_index('ix_referrals_referral_code', 'referrals', ['referral_code'])


def downgrade() -> None:
    """Drop referrals table."""
    op.drop_index('ix_referrals_referral_code', table_name='referrals')
    op.drop_index('ix_referrals_referred_user_id', table_name='referrals')
    op.drop_index('ix_referrals_referrer_user_id', table_name='referrals')
    op.drop_table('referrals')

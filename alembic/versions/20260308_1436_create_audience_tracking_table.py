"""Create audience tracking subscriptions table.

Revision ID: 20260308_1436
Revises: 20260308_0001
Create Date: 2026-03-08 14:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260308_1436'
down_revision: Union[str, None] = '20260308_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audience_tracking_subscriptions table."""
    op.create_table(
        'audience_tracking_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('target_username', sa.String(length=255), nullable=False),
        sa.Column('target_user_id', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('auto_renew', sa.Boolean(), nullable=False, default=False),
        sa.Column('payment_id', sa.Integer(), nullable=True),
        sa.Column('amount_paid', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('last_follower_count', sa.Integer(), nullable=True),
        sa.Column('last_following_count', sa.Integer(), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_audience_tracking_user_id', 'audience_tracking_subscriptions', ['user_id'])
    op.create_index('ix_audience_tracking_target_username', 'audience_tracking_subscriptions', ['target_username'])
    op.create_index('ix_audience_tracking_is_active', 'audience_tracking_subscriptions', ['is_active'])
    op.create_index('ix_audience_tracking_expires_at', 'audience_tracking_subscriptions', ['expires_at'])


def downgrade() -> None:
    """Drop audience_tracking_subscriptions table."""
    op.drop_index('ix_audience_tracking_expires_at', table_name='audience_tracking_subscriptions')
    op.drop_index('ix_audience_tracking_is_active', table_name='audience_tracking_subscriptions')
    op.drop_index('ix_audience_tracking_target_username', table_name='audience_tracking_subscriptions')
    op.drop_index('ix_audience_tracking_user_id', table_name='audience_tracking_subscriptions')
    op.drop_table('audience_tracking_subscriptions')

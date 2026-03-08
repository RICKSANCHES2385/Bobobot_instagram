"""Create subscriptions table

Revision ID: 003
Revises: 002
Create Date: 2026-03-08 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create subscriptions table."""
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('type', sa.Enum('TRIAL', 'BASIC', 'PREMIUM', name='subscriptiontypeenum'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'EXPIRED', 'CANCELLED', name='subscriptionstatusenum'), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('price_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('price_currency', sa.String(3), nullable=False),
        sa.Column('auto_renew', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    op.create_index('ix_subscriptions_user_status', 'subscriptions', ['user_id', 'status'])


def downgrade() -> None:
    """Drop subscriptions table."""
    op.drop_index('ix_subscriptions_user_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_status', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')
    
    # Drop enums (PostgreSQL specific)
    op.execute('DROP TYPE IF EXISTS subscriptionstatusenum')
    op.execute('DROP TYPE IF EXISTS subscriptiontypeenum')

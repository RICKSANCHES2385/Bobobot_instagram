"""Create instagram_requests table

Revision ID: 20260308_1535
Revises: 20260308_1515
Create Date: 2026-03-08 15:35:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260308_1535'
down_revision: Union[str, None] = '20260308_1515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create instagram_requests table."""
    op.create_table(
        'instagram_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(50), nullable=False, index=True),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('target_username', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, index=True),
    )
    
    # Create composite indexes
    op.create_index(
        'idx_user_created',
        'instagram_requests',
        ['user_id', 'created_at']
    )
    op.create_index(
        'idx_user_type',
        'instagram_requests',
        ['user_id', 'request_type']
    )
    op.create_index(
        'idx_status',
        'instagram_requests',
        ['status']
    )


def downgrade() -> None:
    """Drop instagram_requests table."""
    op.drop_index('idx_status', 'instagram_requests')
    op.drop_index('idx_user_type', 'instagram_requests')
    op.drop_index('idx_user_created', 'instagram_requests')
    op.drop_table('instagram_requests')

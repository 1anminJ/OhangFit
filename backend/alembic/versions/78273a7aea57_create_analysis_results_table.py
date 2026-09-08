"""create analysis_results table

Revision ID: 78273a7aea57
Revises: 6e29d7a41811
Create Date: 2026-09-07 21:13:21.032933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78273a7aea57'
down_revision: Union[str, Sequence[str], None] = '6e29d7a41811'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('analysis_results',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('profile_id', sa.UUID(), nullable=False),
    sa.Column('five_elements', sa.JSON(), nullable=False),
    sa.Column('missing_elements', sa.JSON(), nullable=False),
    sa.Column('excess_elements', sa.JSON(), nullable=False),
    sa.Column('sinsal', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('profile_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('analysis_results')

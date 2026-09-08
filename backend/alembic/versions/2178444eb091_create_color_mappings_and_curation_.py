"""create color_mappings and curation_items tables

Revision ID: 2178444eb091
Revises: 78273a7aea57
Create Date: 2026-09-08 15:26:05.501800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2178444eb091'
down_revision: Union[str, Sequence[str], None] = '78273a7aea57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('color_mappings',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('element', sa.String(length=10), nullable=False),
    sa.Column('color_name', sa.String(length=50), nullable=False),
    sa.Column('hex_code', sa.String(length=7), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('curation_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('element', sa.String(length=10), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('image_url', sa.String(length=500), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('curation_items')
    op.drop_table('color_mappings')

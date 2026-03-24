"""remove agent_restricted

Revision ID: 4dc2c0ff8fa2
Revises: 3d5a9da45eb3
Create Date: 2026-03-23 12:32:06.330074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4dc2c0ff8fa2'
down_revision: Union[str, Sequence[str], None] = '3d5a9da45eb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("village", "agent_restricted")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("village", sa.Column("agent_restricted", sa.Boolean(), nullable=True))

"""correct customer name length to 150

Revision ID: 571b19c0a67a
Revises: 276e863b5949
Create Date: 2026-01-01 22:05:49.475892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '571b19c0a67a'
down_revision: Union[str, Sequence[str], None] = '276e863b5949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.alter_column(
        "customer",
        "name",
        type_=sa.VARCHAR(150)
    )


def downgrade():
    op.alter_column(
        "customer",
        "name",
        type_=sa.VARCHAR()
    )
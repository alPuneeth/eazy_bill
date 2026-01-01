"""add varchar limits to customer columns

Revision ID: 276e863b5949
Revises: b3ab1ca14c5c
Create Date: 2026-01-01 22:01:17.214757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '276e863b5949'
down_revision: Union[str, Sequence[str], None] = 'b3ab1ca14c5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "customer",
        "name",
        type_=sa.VARCHAR(100)
    )
    op.alter_column(
        "customer",
        "phone",
        type_=sa.VARCHAR(15)
    )


def downgrade():
    op.alter_column(
        "customer",
        "name",
        type_=sa.VARCHAR()
    )
    op.alter_column(
        "customer",
        "phone",
        type_=sa.VARCHAR()
    )


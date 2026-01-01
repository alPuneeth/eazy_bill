"""Update string limits and stb_id type

Revision ID: b3ab1ca14c5c
Revises: ef8c3beeeb69
Create Date: 2026-01-01 16:35:31.926699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3ab1ca14c5c'
down_revision: Union[str, Sequence[str], None] = 'ef8c3beeeb69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        'bill',
        'bill_code',
        existing_type=sa.String(length=30),
        type_=sa.String(length=100),
        existing_nullable=False
    )

    op.alter_column(
        'deviceinfo',
        'account_number',
        existing_type=sa.String(length=30),
        type_=sa.String(length=100),
        existing_nullable=False
    )

    op.alter_column(
        'deviceinfo',
        'stb_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=100),
        existing_nullable=False
    )

    op.alter_column(
        'deviceinfo',
        'vc_number',
        existing_type=sa.String(length=30),
        type_=sa.String(length=100),
        existing_nullable=False
    )

    op.alter_column(
        'deviceinfo',
        'previous_vc_number',
        existing_type=sa.String(length=30),
        type_=sa.String(length=100),
        existing_nullable=True
    )

    op.alter_column(
        'deviceinfo',
        'tv_name',
        existing_type=sa.String(length=50),
        type_=sa.String(length=100),
        existing_nullable=True
    )

    op.alter_column(
        'village',
        'village_code',
        existing_type=sa.String(length=30),
        type_=sa.String(length=100),
        existing_nullable=False
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        'village',
        'village_code',
        existing_type=sa.String(length=100),
        type_=sa.String(length=30),
        existing_nullable=False
    )

    op.alter_column(
        'deviceinfo',
        'tv_name',
        existing_type=sa.String(length=100),
        type_=sa.String(length=50),
        existing_nullable=True
    )

    op.alter_column(
        'deviceinfo',
        'previous_vc_number',
        existing_type=sa.String(length=100),
        type_=sa.String(length=30),
        existing_nullable=True
    )

    op.alter_column(
        'deviceinfo',
        'vc_number',
        existing_type=sa.String(length=100),
        type_=sa.String(length=30),
        existing_nullable=False
    )

    op.alter_column(
        'deviceinfo',
        'account_number',
        existing_type=sa.String(length=100),
        type_=sa.String(length=30),
        existing_nullable=False
    )

    op.alter_column(
        'bill',
        'bill_code',
        existing_type=sa.String(length=100),
        type_=sa.String(length=30),
        existing_nullable=False
    )

    raise RuntimeError(
        "Downgrade not supported: stb_id was converted from INTEGER to STRING"
    )

    # ### end Alembic commands ###

"""drop subscription table

Revision ID: c54bd50ff440
Revises: 8ec9f3b0e73c
Create Date: 2025-12-23 12:44:58.321126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c54bd50ff440'
down_revision: Union[str, Sequence[str], None] = '8ec9f3b0e73c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("subscription")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "subscription",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("public_id", sa.String(), nullable=False, unique=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customer.id"]),
        sa.ForeignKeyConstraint(["package_id"], ["package.id"]),
    )

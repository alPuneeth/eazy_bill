
"""add user_code, update nullability, rename ftth64_code

Revision ID: ce7d96dfe955
Revises: 4dc2c0ff8fa2
Create Date: 2026-04-02 01:30:53.476195
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = 'ce7d96dfe955'
down_revision: Union[str, Sequence[str], None] = '4dc2c0ff8fa2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 🟢 Rename column instead of drop+add (safe, even if testing)
    op.alter_column('customer', 'ftth64_code', new_column_name='ftth_8')

    # 🟢 Recreate index for renamed column
    op.drop_index(op.f('ix_customer_ftth64_code'), table_name='customer')
    op.create_index(op.f('ix_customer_ftth_8'), 'customer', ['ftth_8'], unique=True)

    # 🟢 Nullable change (safe relaxation)
    op.alter_column(
        'deviceinfo',
        'tvtype_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )

    # 🟢 Explicit server default (keep ONLY if intended)
    op.alter_column(
        'deviceinfo',
        'status_id',
        existing_type=sa.INTEGER(),
        server_default=sa.text('1'),   # remove if not needed
        existing_nullable=False
    )

    # 🟢 Add new column
    op.add_column(
        'user',
        sa.Column('user_code', sa.String(length=3), nullable=True)
    )

    # 🟢 Remove old uniqueness on name (only if intentional)
    op.drop_constraint(op.f('uq_user_name'), 'user', type_='unique')

    # 🟢 Add proper unique constraint (better than unique index)
    op.create_unique_constraint('uq_user_user_code', 'user', ['user_code'])


def downgrade() -> None:
    """Downgrade schema."""

    # 🟢 Remove new constraint
    op.drop_constraint('uq_user_user_code', 'user', type_='unique')

    # 🟢 Restore old constraint
    op.create_unique_constraint(op.f('uq_user_name'), 'user', ['name'])

    # 🟢 Drop column
    op.drop_column('user', 'user_code')

    # 🟢 Revert default
    op.alter_column(
        'deviceinfo',
        'status_id',
        existing_type=sa.INTEGER(),
        server_default=None,
        existing_nullable=False
    )

    # 🟢 Revert nullable change
    op.alter_column(
        'deviceinfo',
        'tvtype_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )

    # 🟢 Restore old index
    op.drop_index(op.f('ix_customer_ftth_8'), table_name='customer')
    op.create_index(op.f('ix_customer_ftth64_code'), 'customer', ['ftth64_code'], unique=True)

    # 🟢 Rename column back
    op.alter_column('customer', 'ftth_8', new_column_name='ftth64_code')
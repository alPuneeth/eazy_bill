"""enforce user_code invariants

Revision ID: 8da9b2fca738
Revises: ce7d96dfe955
Create Date: 2026-04-02 14:45:02.290974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8da9b2fca738'
down_revision: Union[str, Sequence[str], None] = 'ce7d96dfe955'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Make user_code NOT NULL
    op.execute("""
        ALTER TABLE "user"
        ALTER COLUMN user_code SET NOT NULL;
    """)

    # 2. Add CHECK constraint
    op.execute("""
        ALTER TABLE "user"
        ADD CONSTRAINT user_role_user_code_check
        CHECK (
            (role = 'ADMIN' AND user_code = 'KVR') OR
            (role = 'TEST_USER' AND user_code = 'TST') OR
            (role = 'AGENT' AND user_code IS NOT NULL AND user_code <> '')
        );
    """)


def downgrade():
    op.execute("""
        ALTER TABLE "user"
        DROP CONSTRAINT user_role_user_code_check;
    """)

    op.execute("""
        ALTER TABLE "user"
        ALTER COLUMN user_code DROP NOT NULL;
    """)

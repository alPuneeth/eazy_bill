"""seed status lookup table

Revision ID: ef8c3beeeb69
Revises: 370c00080b85
Create Date: 2025-12-26 01:27:52.567875

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ef8c3beeeb69'
down_revision: Union[str, Sequence[str], None] = '370c00080b85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
    INSERT INTO status (id, name, created_at, updated_at)
    VALUES
        (1, 'ACTIVE', now(), now()),
        (2, 'INACTIVE', now(), now()),
        (3, 'ARCHIVED', now(), now())
    ON CONFLICT (id) DO NOTHING;
    """)


def downgrade():
    op.execute("""
    DELETE FROM status
    WHERE id IN (1, 2, 3);
    """)

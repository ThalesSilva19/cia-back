"""add user columns

Revision ID: 63723ecbe3c6
Revises: c83a2f1a9117
Create Date: 2025-09-14 13:10:33.448313

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63723ecbe3c6"
down_revision: Union[str, Sequence[str], None] = "c83a2f1a9117"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user", sa.Column("phone_number", sa.String(length=11), nullable=False)
    )
    op.add_column("user", sa.Column("full_name", sa.String(length=255), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "phone_number")
    op.drop_column("user", "full_name")
    pass

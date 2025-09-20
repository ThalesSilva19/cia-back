"""create transaction table

Revision ID: db0410a18510
Revises: 4cde5aefc2ff
Create Date: 2025-09-17 21:42:36.993041

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "db0410a18510"
down_revision: Union[str, Sequence[str], None] = "4cde5aefc2ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("seats", sa.ARRAY(sa.String(length=3)), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("transaction")

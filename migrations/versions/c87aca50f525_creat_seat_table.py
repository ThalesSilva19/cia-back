"""creat seat table

Revision ID: c87aca50f525
Revises: a68f5655b3ff
Create Date: 2025-09-08 20:16:05.820315

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c87aca50f525"
down_revision: Union[str, Sequence[str], None] = "a68f5655b3ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "seat",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("code", sa.String(length=3), nullable=False, unique=True),
        sa.Column("status", sa.String(length=255), nullable=False, default="available"),
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
    pass


def downgrade() -> None:
    op.drop_table("seat")
    pass

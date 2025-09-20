"""add_scopes_column_to_user

Revision ID: 1f8d75c7b58d
Revises: db0410a18510
Create Date: 2025-09-20 16:14:48.908551

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f8d75c7b58d"
down_revision: Union[str, Sequence[str], None] = "db0410a18510"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user",
        sa.Column("scopes", sa.String(), nullable=False, server_default="default"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "scopes")

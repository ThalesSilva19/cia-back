"""add isHalfPrice column

Revision ID: 4cde5aefc2ff
Revises: 63723ecbe3c6
Create Date: 2025-09-17 21:40:35.842893

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4cde5aefc2ff"
down_revision: Union[str, Sequence[str], None] = "63723ecbe3c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "seat",
        sa.Column(
            "isHalfPrice", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("seat", "isHalfPrice")

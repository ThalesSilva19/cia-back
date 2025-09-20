"""rename_ishalfprice_to_is_half_price

Revision ID: 72de7e730e25
Revises: 1f8d75c7b58d
Create Date: 2025-09-20 17:10:02.977404

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "72de7e730e25"
down_revision: Union[str, Sequence[str], None] = "1f8d75c7b58d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("seat", "isHalfPrice", new_column_name="is_half_price")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("seat", "is_half_price", new_column_name="isHalfPrice")

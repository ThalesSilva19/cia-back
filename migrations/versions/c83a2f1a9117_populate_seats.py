"""populate seats

Revision ID: c83a2f1a9117
Revises: c87aca50f525
Create Date: 2025-09-13 15:44:47.603223

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c83a2f1a9117"
down_revision: Union[str, Sequence[str], None] = "c87aca50f525"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Insert all seats: code A1-A36, B1-B36, ..., P1-P36, Q1-Q30, R1-R26 (total 620 seats)
    conn = op.get_bind()
    seat_rows = []

    # A to P: 1-36
    for letter in [chr(c) for c in range(ord("A"), ord("P") + 1)]:
        for num in range(1, 37):
            code = f"{letter}{num}"
            seat_rows.append({"code": code, "status": "available"})

    # Q: 1-30
    for num in range(1, 31):
        code = f"Q{num}"
        seat_rows.append({"code": code, "status": "available"})

    # R: 1-26
    for num in range(1, 27):
        code = f"R{num}"
        seat_rows.append({"code": code, "status": "available"})

    # Bulk insert
    op.bulk_insert(
        sa.table(
            "seat",
            sa.column("code", sa.String),
            sa.column("status", sa.String),
        ),
        seat_rows,
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM seat"))
    pass

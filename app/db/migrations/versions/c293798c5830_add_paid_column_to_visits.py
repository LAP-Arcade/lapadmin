"""add paid column to visits

Revision ID: c293798c5830
Revises: 9783e35f3a94
Create Date: 2026-07-15 15:19:46.586881

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c293798c5830"
down_revision: Union[str, None] = "9783e35f3a94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("paid", sa.Boolean(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.drop_column("paid")

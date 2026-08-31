"""Track invitees as their own visits, linked via invited_by

Revision ID: d822cdadf484
Revises: 32b5fc24f789
Create Date: 2026-08-31 20:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d822cdadf484"
down_revision: Union[str, None] = "32b5fc24f789"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.add_column(sa.Column("id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("invited_by_id", sa.Integer(), nullable=True)
        )
        batch_op.alter_column(
            "visitor_id", existing_type=sa.Integer(), nullable=True
        )
        batch_op.create_primary_key(batch_op.f("pk_visits"), ["id"])
        batch_op.create_foreign_key(
            batch_op.f("fk_visits_invited_by_id_visitors"),
            "visitors",
            ["invited_by_id"],
            ["id"],
        )


def downgrade() -> None:
    op.execute("DELETE FROM visits WHERE visitor_id IS NULL")
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_visits_invited_by_id_visitors"), type_="foreignkey"
        )
        batch_op.drop_constraint(batch_op.f("pk_visits"), type_="primary")
        batch_op.alter_column(
            "visitor_id", existing_type=sa.Integer(), nullable=False
        )
        batch_op.drop_column("invited_by_id")
        batch_op.drop_column("id")

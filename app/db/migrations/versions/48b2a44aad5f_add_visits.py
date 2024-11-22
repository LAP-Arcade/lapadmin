"""add visits

Revision ID: 48b2a44aad5f
Revises: 3f8661a94b71
Create Date: 2024-10-26 19:43:20.199463

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "48b2a44aad5f"
down_revision: Union[str, None] = "3f8661a94b71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_visits_opening_id_openings"),
            "openings",
            ["opening_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_visits_visitor_id_visitors"),
            "visitors",
            ["visitor_id"],
            ["id"],
        )
        batch_op.drop_column("id")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.add_column(sa.Column("id", sa.INTEGER(), nullable=False))
        batch_op.drop_constraint(
            batch_op.f("fk_visits_visitor_id_visitors"), type_="foreignkey"
        )
        batch_op.drop_constraint(
            batch_op.f("fk_visits_opening_id_openings"), type_="foreignkey"
        )

    # ### end Alembic commands ###
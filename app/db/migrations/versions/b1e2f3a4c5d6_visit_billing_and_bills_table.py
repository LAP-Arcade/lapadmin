"""visit billing and bills table

Revision ID: b1e2f3a4c5d6
Revises: c293798c5830
Create Date: 2026-07-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b1e2f3a4c5d6"
down_revision: Union[str, None] = "c293798c5830"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("billed_amount", sa.Float(), nullable=True)
        )
        batch_op.add_column(sa.Column("note", sa.String(), nullable=True))

    op.drop_table("pricings")

    op.create_table(
        "bills",
        sa.Column("service", sa.Enum("SUMUP", name="service"), nullable=False),
        sa.Column("reference", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bills")),
    )

    op.create_table(
        "bill_visits",
        sa.Column("bill_id", sa.Integer(), nullable=False),
        sa.Column("visitor_id", sa.Integer(), nullable=False),
        sa.Column("opening_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["bill_id"], ["bills.id"], name=op.f("fk_bill_visits_bill_id_bills")
        ),
        sa.ForeignKeyConstraint(
            ["opening_id"],
            ["openings.id"],
            name=op.f("fk_bill_visits_opening_id_openings"),
        ),
        sa.ForeignKeyConstraint(
            ["visitor_id"],
            ["visitors.id"],
            name=op.f("fk_bill_visits_visitor_id_visitors"),
        ),
        sa.PrimaryKeyConstraint(
            "bill_id", "visitor_id", "opening_id", name=op.f("pk_bill_visits")
        ),
    )


def downgrade() -> None:
    op.drop_table("bill_visits")
    op.drop_table("bills")

    op.create_table(
        "pricings",
        sa.Column("name", sa.VARCHAR(), nullable=False),
        sa.Column("price", sa.FLOAT(), nullable=False),
        sa.Column("type", sa.VARCHAR(length=6), nullable=False),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_pricings")),
    )

    with op.batch_alter_table("visits", schema=None) as batch_op:
        batch_op.drop_column("note")
        batch_op.drop_column("billed_amount")

"""Simplify bill visits join on visit id

Revision ID: 23d1ce2fb8bc
Revises: d822cdadf484
Create Date: 2026-08-31 20:05:55.070891

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "23d1ce2fb8bc"
down_revision: Union[str, None] = "d822cdadf484"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("bill_visits", schema=None) as batch_op:
        batch_op.add_column(sa.Column("visit_id", sa.Integer(), nullable=True))

    op.execute(
        "UPDATE bill_visits SET visit_id = ("
        "SELECT id FROM visits"
        " WHERE visits.visitor_id = bill_visits.visitor_id"
        " AND visits.opening_id = bill_visits.opening_id"
        ")"
    )
    op.execute("DELETE FROM bill_visits WHERE visit_id IS NULL")

    with op.batch_alter_table("bill_visits", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_bill_visits_visitor_id_visitors"), type_="foreignkey"
        )
        batch_op.drop_constraint(
            batch_op.f("fk_bill_visits_opening_id_openings"), type_="foreignkey"
        )
        batch_op.drop_constraint(batch_op.f("pk_bill_visits"), type_="primary")
        batch_op.alter_column(
            "visit_id", existing_type=sa.Integer(), nullable=False
        )
        batch_op.create_primary_key(
            batch_op.f("pk_bill_visits"), ["bill_id", "visit_id"]
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_bill_visits_visit_id_visits"),
            "visits",
            ["visit_id"],
            ["id"],
        )
        batch_op.drop_column("opening_id")
        batch_op.drop_column("visitor_id")


def downgrade() -> None:
    with op.batch_alter_table("bill_visits", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("visitor_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("opening_id", sa.Integer(), nullable=True)
        )

    op.execute(
        "DELETE FROM bill_visits WHERE visit_id IN ("
        "SELECT id FROM visits WHERE visitor_id IS NULL"
        ")"
    )
    op.execute(
        "UPDATE bill_visits SET"
        " visitor_id = (SELECT visitor_id FROM visits WHERE visits.id = bill_visits.visit_id),"
        " opening_id = (SELECT opening_id FROM visits WHERE visits.id = bill_visits.visit_id)"
    )

    with op.batch_alter_table("bill_visits", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_bill_visits_visit_id_visits"), type_="foreignkey"
        )
        batch_op.drop_constraint(batch_op.f("pk_bill_visits"), type_="primary")
        batch_op.alter_column(
            "visitor_id", existing_type=sa.Integer(), nullable=False
        )
        batch_op.alter_column(
            "opening_id", existing_type=sa.Integer(), nullable=False
        )
        batch_op.create_primary_key(
            batch_op.f("pk_bill_visits"),
            ["bill_id", "visitor_id", "opening_id"],
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_bill_visits_opening_id_openings"),
            "openings",
            ["opening_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_bill_visits_visitor_id_visitors"),
            "visitors",
            ["visitor_id"],
            ["id"],
        )
        batch_op.drop_column("visit_id")

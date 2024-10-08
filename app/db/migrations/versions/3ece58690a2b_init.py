"""init

Revision ID: 3ece58690a2b
Revises:
Create Date: 2024-10-02 23:58:56.321407

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3ece58690a2b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "bookings",
        sa.Column("visitor_id", sa.Integer(), nullable=False),
        sa.Column("opening_id", sa.Integer(), nullable=False),
        sa.Column("extras", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bookings")),
    )
    op.create_table(
        "openings",
        sa.Column("start", sa.DateTime(), nullable=False),
        sa.Column("end", sa.DateTime(), nullable=False),
        sa.Column(
            "scope",
            sa.Enum("PUBLIC", "PRIVATE", name="scope"),
            server_default="public",
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_openings")),
    )
    op.create_table(
        "pricings",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column(
            "type", sa.Enum("hourly", "entry", name="type"), nullable=False
        ),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_pricings")),
    )
    op.create_table(
        "staffings",
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("opening_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_staffings")),
    )
    op.create_table(
        "staffs",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_staffs")),
    )
    op.create_table(
        "visitors",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_visitors")),
    )
    op.create_table(
        "visits",
        sa.Column("visitor_id", sa.Integer(), nullable=False),
        sa.Column("opening_id", sa.Integer(), nullable=False),
        sa.Column("entry", sa.DateTime(), nullable=True),
        sa.Column("exit", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_visits")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("visits")
    op.drop_table("visitors")
    op.drop_table("staffs")
    op.drop_table("staffings")
    op.drop_table("pricings")
    op.drop_table("openings")
    op.drop_table("bookings")
    # ### end Alembic commands ###

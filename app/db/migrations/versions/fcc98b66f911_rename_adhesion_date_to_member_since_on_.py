"""rename adhesion_date to member_since on visitors

Revision ID: fcc98b66f911
Revises: 41bc38f05eeb
Create Date: 2026-08-23 03:27:07.065517

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fcc98b66f911"
down_revision: Union[str, None] = "41bc38f05eeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("visitors", schema=None) as batch_op:
        batch_op.alter_column("adhesion_date", new_column_name="member_since")


def downgrade() -> None:
    with op.batch_alter_table("visitors", schema=None) as batch_op:
        batch_op.alter_column("member_since", new_column_name="adhesion_date")

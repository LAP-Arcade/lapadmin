"""convert auth_tokens created to utc

Revision ID: 32b5fc24f789
Revises: fcc98b66f911
Create Date: 2026-08-23 04:13:38.038355

"""

from datetime import UTC, datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "32b5fc24f789"
down_revision: Union[str, None] = "fcc98b66f911"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # `created` was previously written with naive datetime.now() (local
    # server time). Reinterpret each value as local time, convert to UTC,
    # and store it back naive (SQLite has no timezone-aware storage).
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, created FROM auth_tokens")
    ).fetchall()
    for id_, created in rows:
        if created is None:
            continue
        local = datetime.fromisoformat(created)
        utc = local.astimezone(UTC).replace(tzinfo=None)
        conn.execute(
            sa.text("UPDATE auth_tokens SET created = :created WHERE id = :id"),
            {"created": utc.isoformat(sep=" "), "id": id_},
        )


def downgrade() -> None:
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id, created FROM auth_tokens")
    ).fetchall()
    for id_, created in rows:
        if created is None:
            continue
        utc = datetime.fromisoformat(created).replace(tzinfo=UTC)
        local = utc.astimezone().replace(tzinfo=None)
        conn.execute(
            sa.text("UPDATE auth_tokens SET created = :created WHERE id = :id"),
            {"created": local.isoformat(sep=" "), "id": id_},
        )

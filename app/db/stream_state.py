import datetime

from . import Column, Id, Table, column


class StreamState(Table, Id):
    game: Column[str] = column(unique=True)
    inactive_since: Column[datetime.datetime | None] = column(
        nullable=True, default=None
    )

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy.ext.hybrid import hybrid_property

from . import Column, Id, Table, column, relation

if TYPE_CHECKING:
    from . import Payment, Visit


class Visitor(Table, Id):
    _first_name: Column[str] = column("first_name", nullable=True)
    _last_name: Column[str] = column("last_name", nullable=True)
    nick: Column[str] = column(nullable=True)
    email: Column[str] = column(nullable=True)
    adhesion_date: Column[date | None] = column(nullable=True, default=None)
    deleted_at: Column[datetime | None] = column(nullable=True, default=None)

    visits: Column[list["Visit"]] = relation("Visit", back_populates="visitor")

    @property
    def first_name(self):
        if self.is_deleted:
            return "[REDACTED]"
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value

    @property
    def last_name(self):
        if self.is_deleted:
            return "[REDACTED]"
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value

    @property
    def full_name(self):
        if self.is_deleted:
            return "[REDACTED]"
        if not self.first_name:
            return self.last_name
        if not self.last_name:
            return self.first_name
        return f"{self.first_name} {self.last_name}"

    @property
    def input(self):
        return f"{self} (#{self.id})"

    @property
    def is_incomplete(self):
        return not self.is_deleted and not bool(self.first_name and self.last_name and self.email)

    @hybrid_property
    def is_deleted(self):
        return self.deleted_at != None  # noqa: E711

    def __gt__(self, other):
        def key(visitor):
            return (visitor.nick or visitor.full_name or visitor.email).lower()

        return key(self) > key(other)

    def __str__(self):
        name = self.full_name or self.email.split("@")[0]
        if self.nick:
            if not name:
                return self.nick
            name += f' "{self.nick}"'
        return name or "Empty"


def get_input_list():
    from app import app

    with app.session() as s:
        return [
            v.input
            for v in sorted(
                s.query(Visitor).filter(~Visitor.is_deleted),
                key=lambda x: str(x).lower(),
            )
        ]

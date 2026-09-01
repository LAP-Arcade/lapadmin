from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy.ext.hybrid import hybrid_property

from . import Column, Id, Table, column, relation

if TYPE_CHECKING:
    from . import Visit


class Visitor(Table, Id):
    _first_name: Column[str] = column("first_name", nullable=True)
    _last_name: Column[str] = column("last_name", nullable=True)
    _nick: Column[str] = column("nick", nullable=True)
    email: Column[str] = column(nullable=True)
    member_since: Column[date | None] = column(nullable=True, default=None)
    deleted_at: Column[datetime | None] = column(nullable=True, default=None)
    self_edit_uuid: Column[str | None] = column(nullable=True, default=None)

    visits: Column[list["Visit"]] = relation(
        "Visit",
        foreign_keys="Visit.visitor_id",
        back_populates="visitor",
        cascade="all, delete-orphan",
    )
    invitees: Column[list["Visit"]] = relation(
        "Visit",
        foreign_keys="Visit.invited_by_id",
        back_populates="invited_by",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def first_name(self):
        if self.is_deleted:
            return "[REDACTED]"
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = value

    @first_name.expression
    def first_name(cls):
        return cls._first_name

    @hybrid_property
    def last_name(self):
        if self.is_deleted:
            return "[REDACTED]"
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = value

    @last_name.expression
    def last_name(cls):
        return cls._last_name

    @hybrid_property
    def nick(self):
        if self.is_deleted:
            return "[REDACTED]"
        return self._nick

    @nick.setter
    def nick(self, value):
        self._nick = value

    @nick.expression
    def nick(cls):
        return cls._nick

    @property
    def short_name(self):
        if self.is_deleted:
            return "[REDACTED]"
        if self.nick:
            return self.nick
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name
        if self.email:
            return self.email.split("@")[0]
        return "Empty"

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
    def long_name(self):
        name = self.full_name or self.email.split("@")[0]
        if self.nick:
            if not name:
                return self.nick
            name += f' "{self.nick}"'
        return name or "Empty"

    @property
    def input(self):
        return f"{self} (#{self.id})"

    @property
    def is_incomplete(self):
        if self.is_deleted:
            return False

        return not bool(self.first_name and self.last_name and self.email)

    @property
    def is_member(self):
        return self.member_since is not None

    def mark_as_member(self):
        if not self.member_since:
            self.member_since = date.today()

    @hybrid_property
    def is_deleted(self):
        return self.deleted_at != None  # noqa: E711

    def __gt__(self, other):
        def key(visitor):
            return (visitor.nick or visitor.full_name or visitor.email).lower()

        return key(self) > key(other)

    def __str__(self):
        return self.short_name


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

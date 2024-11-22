from typing import TYPE_CHECKING

from . import Column, Id, Table, column, relation

if TYPE_CHECKING:
    from . import Visit


class Visitor(Table, Id):
    first_name: Column[str] = column(nullable=True)
    last_name: Column[str] = column(nullable=True)
    nick: Column[str] = column(nullable=True)
    email: Column[str] = column(nullable=True)

    visits: Column[list["Visit"]] = relation("Visit", back_populates="visitor")

    @property
    def full_name(self):
        if not self.first_name:
            return self.last_name
        if not self.last_name:
            return self.first_name
        return f"{self.first_name} {self.last_name}"

    @property
    def is_incomplete(self):
        return not bool(self.first_name or self.last_name or self.email)

    def __str__(self):
        name = self.full_name or self.email.split("@")[0]
        if self.nick:
            if not name:
                return self.nick
            name += f' "{self.nick}"'
        return name or "Empty"

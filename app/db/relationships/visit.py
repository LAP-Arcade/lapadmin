from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from .. import Column, ForeignKey, Table, column, relation

if TYPE_CHECKING:
    from .. import Opening, Visitor


class Visit(Table):
    visitor_id = column(ForeignKey("visitors.id"), primary_key=True)
    opening_id = column(ForeignKey("openings.id"), primary_key=True)

    visitor: Column[Visitor] = relation("Visitor", back_populates="visits")
    opening: Column[Opening] = relation("Opening", back_populates="visits")

    entry: Column[datetime.datetime] = column(nullable=True)
    exit: Column[datetime.datetime] = column(nullable=True)

    @property
    def finished(self) -> bool:
        return self.exit is not None

    @property
    def paid(self) -> bool:
        # TODO fetch relationship payment with item type entry
        return False

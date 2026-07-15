from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from .. import Column, ForeignKey, Table, column, relation

BILLING_SEGMENT_MINUTES = 30
BILLING_MINIMUM_MINUTES = 10
ENTRY_PRICE_PER_HOUR = 3

if TYPE_CHECKING:
    from .. import Opening, Visitor


class Visit(Table):
    visitor_id = column(ForeignKey("visitors.id"), primary_key=True)
    opening_id = column(ForeignKey("openings.id"), primary_key=True)

    visitor: Column[Visitor] = relation("Visitor", back_populates="visits")
    opening: Column[Opening] = relation("Opening", back_populates="visits")

    entry: Column[datetime.datetime] = column(nullable=True)
    exit: Column[datetime.datetime] = column(nullable=True)
    paid: Column[bool] = column(default=False, nullable=False)

    @property
    def finished(self) -> bool:
        return self.exit is not None

    @property
    def duration(self) -> datetime.timedelta:
        return self.exit - self.entry

    @property
    def billed_duration(self) -> datetime.timedelta | None:
        if not self.entry or not self.exit:
            return None
        total_minutes = self.duration.total_seconds() / 60
        full_segments = int(total_minutes // BILLING_SEGMENT_MINUTES)
        remainder = total_minutes % BILLING_SEGMENT_MINUTES
        if full_segments == 0:
            billed_segments = 1
        elif remainder > BILLING_MINIMUM_MINUTES:
            billed_segments = full_segments + 1
        else:
            billed_segments = full_segments
        return datetime.timedelta(
            minutes=billed_segments * BILLING_SEGMENT_MINUTES
        )

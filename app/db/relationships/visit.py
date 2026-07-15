from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from .. import Column, ForeignKey, Table, column, relation

BILLING_SEGMENT_MINUTES = 30
BILLING_MINIMUM_MINUTES = 10
BILLING_MAX_MINUTES = 240
ENTRY_PRICE_PER_HOUR = 3

if TYPE_CHECKING:
    from .. import Opening, Visitor
    from ..bill import Bill


class Visit(Table):
    visitor_id = column(ForeignKey("visitors.id"), primary_key=True)
    opening_id = column(ForeignKey("openings.id"), primary_key=True)

    visitor: Column[Visitor] = relation("Visitor", back_populates="visits")
    opening: Column[Opening] = relation("Opening", back_populates="visits")
    bills: Column[list[Bill]] = relation(
        "Bill",
        secondary="bill_visits",
        primaryjoin=(
            "and_(foreign(bill_visits.c.visitor_id) == Visit.visitor_id,"
            " foreign(bill_visits.c.opening_id) == Visit.opening_id)"
        ),
        secondaryjoin="Bill.id == foreign(bill_visits.c.bill_id)",
        back_populates="visits",
    )

    entry: Column[datetime.datetime] = column(nullable=True)
    exit: Column[datetime.datetime] = column(nullable=True)
    paid: Column[bool] = column(default=False, nullable=False)
    billed_amount: Column[float] = column(nullable=True)
    note: Column[str] = column(nullable=True)

    @property
    def computed_price(self) -> float | None:
        if self.billed_duration is None:
            return None
        return (
            self.billed_duration.total_seconds() / 3600 * ENTRY_PRICE_PER_HOUR
        )

    @property
    def effective_price(self) -> float | None:
        if self.billed_amount is not None:
            return self.billed_amount
        return self.computed_price

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
        if total_minutes < 0:
            return None
        total_minutes = min(total_minutes, BILLING_MAX_MINUTES)
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

import enum
from enum import StrEnum

import sqlalchemy as sa

from . import Column, ForeignKey, Id, Table, column, relation

bill_visits = sa.Table(
    "bill_visits",
    Table.metadata,
    sa.Column(
        "bill_id", sa.Integer, sa.ForeignKey("bills.id"), primary_key=True
    ),
    sa.Column(
        "visitor_id", sa.Integer, sa.ForeignKey("visitors.id"), primary_key=True
    ),
    sa.Column(
        "opening_id", sa.Integer, sa.ForeignKey("openings.id"), primary_key=True
    ),
)


class Bill(Table, Id):
    class Service(StrEnum):
        SUMUP = "SumUp"

    service: Column[Service]
    reference: Column[str]

    visits = relation(
        "Visit",
        secondary=bill_visits,
        primaryjoin="Bill.id == foreign(bill_visits.c.bill_id)",
        secondaryjoin=(
            "and_(foreign(bill_visits.c.visitor_id) == Visit.visitor_id,"
            " foreign(bill_visits.c.opening_id) == Visit.opening_id)"
        ),
        back_populates="bills",
    )

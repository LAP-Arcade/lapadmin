from enum import StrEnum

import sqlalchemy as sa

from . import Column, Id, Table, relation

bill_visits = sa.Table(
    "bill_visits",
    Table.metadata,
    sa.Column(
        "bill_id", sa.Integer, sa.ForeignKey("bills.id"), primary_key=True
    ),
    sa.Column(
        "visit_id", sa.Integer, sa.ForeignKey("visits.id"), primary_key=True
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
        back_populates="bills",
    )

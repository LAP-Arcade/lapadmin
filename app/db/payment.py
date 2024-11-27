import enum
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from . import Column, ForeignKey, Id, Table, column, relation

if TYPE_CHECKING:
    from .staff import Staff
    from .visitor import Visitor


class Payment(Table, Id):
    class Method(StrEnum):
        CASH = enum.auto()
        CARD = enum.auto()
        PAYPAL = enum.auto()
        FREE = enum.auto()
        OTHER = enum.auto()

    charged_amount: Column[float]
    received_amount: Column[float]
    text: Column[str]
    note: Column[str]
    time: Column[datetime]
    method: Column[Method]

    charged_by = column(ForeignKey("staffs.id"))
    paid_by = column(ForeignKey("visitors.id"))

    staff: Column["Staff"] = relation("Staff", back_populates="payments")
    visitor: Column["Visitor"] = relation("Visitor", back_populates="payments")

import datetime
import enum
from enum import StrEnum
from typing import TYPE_CHECKING

from . import Column, ForeignKey, Table, column, relation

if TYPE_CHECKING:
    from .staff import Staff


class Availability(Table):
    class Type(StrEnum):
        OPENING = enum.auto()
        CLOSING = enum.auto()
        ALL_DAY = enum.auto()

    staff_id = column(ForeignKey("staff.id"), primary_key=True)
    date: Column[datetime.date] = column(primary_key=True)
    type: Column[Type]

    staff: Column["Staff"] = relation("Staff", back_populates="availabilities")

    def __str__(self):
        return f"{self.staff}: {self.type}"

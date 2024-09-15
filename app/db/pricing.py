import enum
from enum import StrEnum

from . import Column, Table, column


class Pricing(Table):
    class Type(StrEnum):
        hourly = enum.auto()
        entry = enum.auto()

    name: Column[str] = column(primary_key=True)
    price: Column[float]
    type: Column[Type]

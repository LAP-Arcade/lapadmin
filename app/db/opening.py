import datetime
import enum
from enum import StrEnum

from . import Column, Id, Table, column


class Opening(Table, Id):
    class Scope(StrEnum):
        PUBLIC = enum.auto()
        PRIVATE = enum.auto()

        def __str__(self):
            return self.name.upper()

    start: Column[datetime.datetime]
    end: Column[datetime.datetime]
    scope: Column[Scope] = column(default=Scope.PUBLIC)

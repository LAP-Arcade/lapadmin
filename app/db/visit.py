import datetime

from . import Column, Id, Table


class Visit(Table, Id):
    visitor_id: Column[int]
    opening_id: Column[int]
    entry: Column[datetime.datetime | None]
    exit: Column[datetime.datetime | None]

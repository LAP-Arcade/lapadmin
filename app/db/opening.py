import datetime

from . import Column, Id, Table


class Opening(Table, Id):
    start: Column[datetime.datetime]
    end: Column[datetime.datetime]

from . import Column, Id, Table, column


class Booking(Table, Id):
    visitor_id: Column[int]
    opening_id: Column[int]
    extras: Column[int] = column(default=0)

from . import Column, Id, Table


class Staffing(Table, Id):
    staff_id: Column[int]
    opening_id: Column[int]

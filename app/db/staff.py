from . import Column, Id, Table


class Staff(Table, Id):
    name: Column[str]

from . import Column, Id, Table


class Visitor(Table, Id):
    name: Column[str]
    email: Column[str]

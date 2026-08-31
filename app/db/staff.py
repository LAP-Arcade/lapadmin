from typing import TYPE_CHECKING

from . import Column, Id, Table, column, relation

if TYPE_CHECKING:
    from .auth_token import AuthToken
    from .availability import Availability


class Staff(Table, Id):
    __tablename__ = "staff"

    name: Column[str]
    discord_id: Column[str] = column(unique=True)

    tokens: Column[list["AuthToken"]] = relation(
        "AuthToken", back_populates="staff"
    )
    availabilities: Column[list["Availability"]] = relation(
        "Availability", back_populates="staff"
    )

    def __str__(self):
        return self.name

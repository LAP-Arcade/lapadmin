from typing import TYPE_CHECKING

from . import Column, Id, Table, column, relation

if TYPE_CHECKING:
    from .auth_token import AuthToken
    from .payment import Payment


class Staff(Table, Id):
    name: Column[str]
    discord_id: Column[str] = column(unique=True)

    tokens: Column[list["AuthToken"]] = relation(
        "AuthToken", back_populates="staff"
    )
    payments: Column[list["Payment"]] = relation(
        "Payment", back_populates="staff"
    )

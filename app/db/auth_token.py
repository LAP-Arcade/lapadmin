import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from . import Column, ForeignKey, Id, Table, column, relation

if TYPE_CHECKING:
    from .staff import Staff


class AuthToken(Table, Id):
    staff_id = column(ForeignKey("staffs.id"))
    token: Column[str] = column(nullable=False)
    created: Column[datetime] = column(default=datetime.now)

    staff: Column["Staff"] = relation("Staff", back_populates="tokens")

    def __init__(self, staff):
        if isinstance(staff, int):
            self.staff_id = staff
        else:
            self.staff_id = staff.id
        self.token = secrets.token_hex(32)

    @property
    def is_valid(self) -> bool:
        return self.created > datetime.now() - timedelta(days=30)

    @property
    def cookie(self) -> str:
        return f"{self.id}-{self.token}"

    @classmethod
    def validate(cls, session, token: str) -> "AuthToken":
        id, token = token.split("-")
        entry = session.query(cls).filter_by(id=id, token=token).first()
        if entry and entry.is_valid:
            return entry
        return None

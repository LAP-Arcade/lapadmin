import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from . import Column, ForeignKey, Id, Table, column, relation

if TYPE_CHECKING:
    from .staff import Staff


class AuthToken(Table, Id):
    staff_id = column(ForeignKey("staffs.id"))
    token: Column[str] = column(nullable=False)
    created: Column[datetime] = column(default=lambda: datetime.now(UTC))

    staff: Column["Staff"] = relation("Staff", back_populates="tokens")

    def __init__(self, staff):
        if isinstance(staff, int):
            self.staff_id = staff
        else:
            self.staff_id = staff.id
        self.token = secrets.token_hex(32)

    @property
    def is_valid(self) -> bool:
        created = self.created.replace(tzinfo=UTC)
        return created > datetime.now(UTC) - timedelta(days=30)

    @property
    def cookie(self) -> str:
        return f"{self.id}-{self.token}"

    @classmethod
    def validate(cls, session, token: str) -> "AuthToken | None":
        parts = token.split("-", 1)
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1]:
            return None
        id, token = parts
        entry = session.query(cls).filter_by(id=id, token=token).first()
        if entry and entry.is_valid:
            return entry
        return None

import dataclasses
import enum
import functools
from dataclasses import dataclass

import yaml

from app import DATA_DIR


@dataclass
class ItemEntry:
    class Billing(enum.StrEnum):
        HOURLY = enum.auto()
        MONTHLY = enum.auto()

    class Type(enum.StrEnum):
        ITEM = enum.auto()
        ENTRY = enum.auto()
        MERCH = enum.auto()
        SUBSCRIPTION = enum.auto()

    name: str
    price: float = 0.0
    id: str = None
    type: Type = Type.ITEM
    max: int = None
    billing: Billing = None
    holder: str = None
    discounts: dict = None
    revshare: float = 0.0

    def __str__(self):
        result = self.name
        if self.type == self.Type.MERCH:
            result += f" ({self.holder})"
        if self.id:
            result += f" (#{self.id})"
        return result

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not value:
                continue
            if isinstance(field.type, enum.EnumMeta):
                setattr(self, field.name, field.type(value))
        if self.revshare and not self.holder:
            raise ValueError(f"revshare requires holder (item: {self.name})")


@functools.cache
def get_all():
    items = []
    for path in (DATA_DIR / "items").rglob("*.yml"):
        with path.open() as f:
            data = yaml.safe_load(f)
        for entry in data:
            if path.parent.name == "merch":
                entry.setdefault("type", ItemEntry.Type.MERCH.value)
                entry.setdefault("holder", path.stem)
            if path.stem == "entries":
                entry.setdefault("type", ItemEntry.Type.ENTRY.value)
            items.append(ItemEntry(**entry))
    return items


@functools.cache
def get_by_id(id):
    for item in get_all():
        if item.id == id:
            return item
    return None


def get_input_list():
    return [str(i) for i in sorted(get_all(), key=lambda x: str(x).lower())]

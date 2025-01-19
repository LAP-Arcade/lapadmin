from typing import TYPE_CHECKING
from . import Column, ForeignKey, Id, Table, column, relation

if TYPE_CHECKING:
    from .cart import Cart


class CartItem(Table, Id):
    cart_id = column(ForeignKey("carts.id"))
    quantity = Column[int]
    item = Column[str]
    price = Column[float]

    cart: Column["Cart"] = relation("Cart", back_populates="cart_items")

from typing import TYPE_CHECKING
from . import Column, ForeignKey, Id, Table, column, relation

if TYPE_CHECKING:
    from .visitor import Visitor
    from .cart_item import CartItem


class Cart(Table, Id):
    visitor_id = column(ForeignKey("visitors.id"))

    visitor: Column["Visitor"] = relation("Visitor", back_populates="carts")
    cart_items: Column[list["CartItem"]] = relation(
        "CartItem", back_populates="cart"
    )

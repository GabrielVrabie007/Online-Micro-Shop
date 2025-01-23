from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    from .order import Order
"""
Permite legarea mai multor produse de mai multe comenzi
Un order (comandă) poate conține multe products (produse)
Un product poate apărea în multe orders

"""


class OrderProductAssociation(Base):
    __tablename__ = "order_product_association_table"
    __table_args__ = tuple(
        UniqueConstraint("order_id", "product_id", name="index_unique_order_product")
    )
    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    quantity: Mapped[int] = mapped_column(default=1, server_default="1")

    unit_price: Mapped[int] = mapped_column(default=0, server_default="0")

    order: Mapped["Order"] = relationship(back_populates="product_details")

    product: Mapped["Product"] = relationship(back_populates="order_details")

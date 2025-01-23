from .base import Base
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .order import Order
    from .order_product_association import OrderProductAssociation


class Product(Base):
    __tablename__ = "products"
    name: Mapped[str]
    price: Mapped[int]
    description: Mapped[str]

    # orders: Mapped[list["Order"]] = relationship(
    #     secondary="order_product_association_table", back_populates="products"
    # )
    order_details: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="product"
    )

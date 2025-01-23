from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product
    from .order_product_association import OrderProductAssociation


class Order(Base):
    __tablename__ = "orders"
    promo_code: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=datetime.now,
    )
    # products: Mapped[list["Product"]] = relationship(
    #     secondary="order_product_association_table",
    #     back_populates="orders",
    # )
    product_details: Mapped[list["OrderProductAssociation"]] = relationship(
        back_populates="order"
    )

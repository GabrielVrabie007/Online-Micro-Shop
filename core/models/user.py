from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class User(Base):
    __tablename__ = "users"
    # Limit length username=20
    username: Mapped[str] = mapped_column(String(20), unique=True)

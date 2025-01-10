from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from .profile import Profile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .post import Post


class User(Base):
    __tablename__ = "users"
    # Limit length username=20
    username: Mapped[str] = mapped_column(String(20), unique=True)
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")
    profile: Mapped["Profile"] = relationship(back_populates="user")

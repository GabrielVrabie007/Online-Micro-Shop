from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict


class CreateUser(BaseModel):
    # username: str = Field(..., min_length=3, max_length=20)
    username: Annotated[str, MinLen(3), MaxLen(20)]
    email: EmailStr


class UserSchema(BaseModel):
    """
    Schema for user data validation and storage.

    Attributes:
        username: User's unique identifier
        password: Hashed password stored as bytes
        email: Optional email address
        active: User account status, defaults to True
    """

    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True

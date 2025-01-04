from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProductBase(BaseModel):
    name: str
    description: str
    price: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductCreate):
    pass


class ProductUpdatePartial(ProductCreate):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None


# from_attributes=True --> poate prelua datele din atributele unui obiect (cum ar fi proprietățile unui obiect dintr-o clasă
class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

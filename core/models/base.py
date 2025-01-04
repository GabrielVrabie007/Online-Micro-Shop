from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped,declared_attr

class Base(DeclarativeBase):
    #Abstract classses are used to define attributes and methods that are common to all classes that inherit from it
    __abstract__ = True
    #because of @declared_attr you don't need to define __tablename__  every time in the class 
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"
    #mapped class attributes are used to define the columns of the table--> id is column
    id:Mapped[int]=mapped_column(primary_key=True)

# Standard library
from enum import Enum
from typing import Optional

# Third-party
from sqlmodel import SQLModel, Field
from sqlalchemy import Enum as SAEnum, Column

# Local modules
from app.models.utilities import TimestampMixin, generate_uuid


class CustomerTypeEnum(str, Enum):
    REGULAR = "regular"
    SPONSORED = "sponsored"


class CustomerType(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(default_factory=generate_uuid, unique=True)
    name: CustomerTypeEnum = Field(sa_column=Column(SAEnum(CustomerTypeEnum),
                                                    unique=True))
    description: Optional[str] = Field(default=None)





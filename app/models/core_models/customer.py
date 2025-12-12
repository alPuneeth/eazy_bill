# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin, generate_uuid


class Customer(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(default_factory=generate_uuid, unique=True)
    name: str
    phone: str = Field(unique=True)
    alternate_number: Optional[str] = Field(default=None)
    aadhaar_number: Optional[str] = Field(default=None)
    upi_id: Optional[str] = Field(default=None)
    village_id: int = Field(foreign_key="village.id")
    customer_type_id: int = Field(foreign_key="customertype.id")
    description: Optional[str] = Field(default=None)

# standard library
from typing import Optional
from datetime import datetime

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin, generate_uuid


class Subscription(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(default_factory=generate_uuid, unique=True)
    customer_id: int = Field(foreign_key="customer.id")
    package_id: int = Field(foreign_key="package.id")
    start_date: datetime
    end_date: datetime
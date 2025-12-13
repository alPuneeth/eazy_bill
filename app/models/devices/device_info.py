# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin, generate_uuid


class DeviceInfo(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(default_factory=generate_uuid, unique=True)
    customer_id: int = Field(foreign_key="customer.id")
    account_number: str
    stb_id: int
    vc_number: str
    previous_vc_number: Optional[str] = Field(default=None)
    ftth64_id: int = Field(foreign_key="ftth64.id")
    tvtype_id: int = Field(foreign_key="tvtype.id")
    status_id: int = Field(foreign_key="status.id")
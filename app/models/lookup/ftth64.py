# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin


class FTTH64(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    code: str
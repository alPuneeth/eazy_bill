# Standard library
from typing import Optional

# Third-party
from sqlmodel import SQLModel, Field

# Local application
from app.models.utilities import TimestampMixin


class Village(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    postal_code: str = Field(index=True)

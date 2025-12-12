# Standard library
from typing import Optional
from enum import Enum

# Third-party
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum as SAEnum

# Local application
from app.models.utilities import TimestampMixin


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Status(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: StatusEnum = Field(sa_column=Column(SAEnum(StatusEnum), unique=True))
    description: Optional[str] = Field(default=None)
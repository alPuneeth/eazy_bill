from sqlmodel import Field
from app.models.base import TimestampMixin
from typing import Optional
from enum import Enum


class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# def utc_now():
#     return datetime.now(timezone.utc)


class StatusModel(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: StatusEnum = Field(unique=True)
    description: str | None = None
# standard library
from datetime import datetime, timezone
import uuid

# third-party library
from sqlmodel import SQLModel, Field


def utc_now():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utc_now)

    # NOTE: Manually update this field using utc_now()
    # before committing any changes.
    updated_at: datetime = Field(default_factory=utc_now)

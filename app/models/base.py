from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc)


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utc_now)

    # NOTE: Manually update this field using utc_now()
    # before committing any changes.
    updated_at: datetime = Field(default_factory=utc_now)

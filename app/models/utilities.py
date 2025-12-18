# standard library
from datetime import datetime, timezone
import uuid

# third-party library
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr


def utc_now():
    return datetime.now(timezone.utc)


def generate_uuid():
    return str(uuid.uuid4())


class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(
                    DateTime(timezone=True),
                    nullable=False,
                    default=utc_now
                    )

    @declared_attr
    def updated_at(cls):
        return Column(
                    DateTime(timezone=True),
                    nullable=False,
                    default=utc_now,
                    onupdate=utc_now
                        )

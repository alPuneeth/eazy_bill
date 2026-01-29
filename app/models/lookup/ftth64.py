# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin


class FTTH64(TimestampMixin, SQLModel, table=True):
    """
    FTTH64 represents an FTTH (Fiber To The Home) service classification
    or plan variant used within the system.

    This model acts as a reference entity that defines available FTTH
    categories by name and code. The code is a human-referenced identifier
    used in lookups, imports, and associations with device or subscription
    records.

    The model defines database structure and integrity only.
    Any service logic or provisioning rules are enforced at the
    application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    name: str = Field(
        ...,
        nullable=False,
        index=True,
        max_length=150
    )

    description: Optional[str] = Field(
        nullable=True,
        default=None
        )

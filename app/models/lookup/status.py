# Standard library
from typing import Optional
from enum import Enum

# Third-party
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum as SAEnum

# Local application
from app.models.utilities import TimestampMixin


class StatusEnum(str, Enum):
    """
    StatusEnum defines the allowed lifecycle states
    for entities within the system.

    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Status(TimestampMixin, SQLModel, table=True):
    """
    Status represents a canonical lifecycle state that can be
    associated with other entities (such as devices or subscriptions).

    This model functions as a reference / lookup table where each
    status value exists exactly once. The enum restricts allowed
    values, and the unique constraint ensures one row per status.

    The model defines database structure and referential integrity only.
    Any behavior tied to status transitions is enforced at the
    application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    # Enum-backed, human-referenced identifier
    # Unique to enforce one row per status value
    name: StatusEnum = Field(
        ...,
        sa_column=Column(SAEnum(StatusEnum),
                         unique=True,
                         nullable=False,
                         )
                         )

    description: Optional[str] = Field(
        default=None,
        nullable=True
        )
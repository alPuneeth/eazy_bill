# Standard library
from enum import Enum
from typing import Optional

# Third-party
from sqlmodel import SQLModel, Field
from sqlalchemy import Enum as SAEnum, Column

# Local modules
from app.models.utilities import TimestampMixin, generate_uuid


def enum_values(enum):
    return [e.value for e in enum]


class CustomerTypeEnum(str, Enum):
    """
    CustomerTypeEnum defines the allowed classifications
    for customers within the system.

    """
    REGULAR = "regular"
    SPONSORED = "sponsored"


class CustomerType(TimestampMixin, SQLModel, table=True):
    """
    CustomerType represents a categorical classification
    assigned to customers.

    This model is used to distinguish customers based on
    predefined business categories such as regular or sponsored.
    The classification is enforced at the database level
    using a constrained enum.

    The model defines structure and referential integrity only.
    Any behavior or rules associated with customer types
    are enforced at the application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    public_id: str = Field(
        ...,
        nullable=False,
        default_factory=generate_uuid,
        unique=True
        )

    name: CustomerTypeEnum = Field(
        ...,
        sa_column=Column(
            SAEnum(
                CustomerTypeEnum,
                name="customertypeenum",
                values_callable=enum_values,
                native_enum=True
                ),
            nullable=False,
            unique=True
            )
        )

    description: Optional[str] = Field(
        default=None,
        nullable=True
        )





# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin, generate_uuid


class Customer(TimestampMixin, SQLModel, table=True):
    """
    Customer represents an individual or entity that receives services
    and is billed within the system.

    This model stores core identification and contact details for a customer,
    along with references to their village and customer type classification.
    Optional fields capture secondary contact or payment identifiers when
    available.

    The model defines structure and database integrity only.
    Any validation, formatting rules, or business logic related to customers
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

    name: str = Field(
        ...,
        index=True,
        nullable=False,
        max_length=50
        )

    phone: str = Field(
        ...,
        index=True,
        nullable=False,
        unique=True,
        max_length=15
        )

    alternate_number: Optional[str] = Field(
        default=None,
        nullable=True
        )

    aadhaar_number: Optional[str] = Field(
        default=None,
        max_length=12,
        nullable=True
        )

    upi_id: Optional[str] = Field(
        default=None,
        nullable=True
        )

    village_id: int = Field(
        ...,
        index=True,
        nullable=False,
        foreign_key="village.id"
        )

    customer_type_id: int = Field(
        ...,
        index=True,
        nullable=False,
        foreign_key="customertype.id"
        )

    description: Optional[str] = Field(
        default=None,
        nullable=True
        )

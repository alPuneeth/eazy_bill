# standard library
from typing import Optional, TYPE_CHECKING

# third-party
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import text

# local module
from app.models.utilities import TimestampMixin, generate_uuid


if TYPE_CHECKING:
    from app.models.core_models.customer import Customer
    from app.models.lookup.status import Status
    from app.models.lookup.tv_type import TVType


class DeviceInfo(TimestampMixin, SQLModel, table=True):
    """
    DeviceInfo represents the physical or logical device details
    associated with subscription or service of a customer.

    This model stores identifiers such as account numbers, VC numbers,
    and device references used for provisioning, tracking, and support.
    It also links the device to its customer, service type, and status.

    The model defines database structure and integrity only.
    Validation rules and provisioning logic are handled at the
    application or service layer.

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

    # FK → Customer (frequently filtered)
    customer_id: int = Field(
        ...,
        index=True,
        nullable=False,
        foreign_key="customer.id",
        unique=True
        )

    account_number: Optional[str] = Field(
        default=None,
        index=True,
        unique=True,
        nullable=True,
        max_length=100
        )

    stb_id: Optional[str] = Field(
        default=None,
        index=True,
        nullable=True,
        )

    vc_number: str = Field(
        ...,
        index=True,
        nullable=False,
        unique=True,
        max_length=100
        )

    previous_vc_number: Optional[str] = Field(
        default=None,
        nullable=True,
        max_length=100
        )

    tv_name: Optional[str] = Field(
        default=None,
        max_length=100,
        nullable=True,
        description="Brand or manufacturer of the TV"
    )

    # FK → TV Type
    tvtype_id: Optional[int] = Field(
        default=None,
        nullable=True,
        index=True,
        foreign_key="tvtype.id"
        )

    # FK → Status
    status_id: int = Field(
        ...,
        nullable=False,
        index=True,
        foreign_key="status.id",
        sa_column_kwargs={"server_default": text("1")}
        )

    customer: Optional["Customer"] = Relationship(back_populates="devices")
    tvtype: "TVType" = Relationship(back_populates="devices")
    status: "Status" = Relationship(back_populates="devices")
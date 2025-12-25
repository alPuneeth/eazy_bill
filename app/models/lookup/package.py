# standard library
from typing import Optional

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin


class Package(TimestampMixin, SQLModel, table=True):
    """
    Package represents a service offering that can be subscribed to
    and billed within the system.

    This model defines the core attributes of a package, including its
    unique name and price. Packages are referenced by subscriptions and
    bills to determine service entitlement and billing amounts.

    The model defines database structure and integrity only.
    Pricing rules, discounts, revisions, or billing behavior are handled
    at the application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    name: str = Field(
        ...,
        nullable=False,
        unique=True,
        index=True
        )

    price: float = Field(
        ...,
        nullable=False,
        index=True
        )

    description: Optional[str] = Field(
        default=None,
        nullable=True
        )

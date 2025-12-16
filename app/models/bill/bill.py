# standard library
from typing import Optional
from datetime import datetime

# third-party
from sqlmodel import SQLModel, Field

# local module
from app.models.utilities import TimestampMixin, generate_uuid


class Bill(TimestampMixin, SQLModel, table=True):
    """
    Bill represents a financial record generated for a customer
    for a specific package over a defined billing period.

    Although a bill is a persisted record, certain fields such as
    start_date, end_date, monthly_count, bill_amount, customer_id,
    and package_id may be modified to correct data entry errors,
    adjust billing periods, or reflect legitimate revisions.

    This model captures billing structure and integrity only.
    Any rules governing when or how modifications are allowed
    are enforced at the application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    public_id: str = Field(
        nullable=False,
        default_factory=generate_uuid,
        unique=True
        )

    customer_id: int = Field(
        ...,
        nullable=False,
        foreign_key="customer.id",
        index=True
        )

    bill_code: str = Field(
        ...,
        nullable=False,
        max_length=10,
        unique=True,
        index=True
        )

    bill_date: datetime = Field(
        ...,
        nullable=False
        )

    package_id: int = Field(
        ...,
        nullable=False, 
        foreign_key="package.id",
        index=True
        )

    monthly_count: int = Field(
        nullable=False,
        default=1
        )

    bill_amount: float = Field(
        ...,
        nullable=False
        )

    start_date: datetime = Field(
        ...,
        nullable=False
        )

    end_date: datetime = Field(
        ...,
        nullable=False
        )

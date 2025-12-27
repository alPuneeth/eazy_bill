from pydantic import BaseModel, Field, model_validator, StringConstraints, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from decimal import Decimal

from app.schemas.common import IdValueRead

BillCodeStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True,
                      min_length=1,
                      max_length=30
                      )
]


class BillCreate(BaseModel):
    bill_code: BillCodeStr
    bill_date: datetime
    start_date: datetime
    end_date: datetime
    monthly_count: int = Field(
        default=1,
        ge=0,
        le=12
        )
    bill_amount: Decimal = Field(
        ge=0,
        examples=[3400, 9332]
        )

    customer_public_id: str
    package_id: int

    @model_validator(mode="after")
    def validate_billing_period(self):
        """
        Ensures the subscription period is logically valid.
        This method runs AFTER all fields are parsed and available.
        """
        # 1. Basic period sanity
        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be after start_date"
            )

        # 2. Ensure bill_date lies within the billing period
        if not (self.start_date <= self.bill_date <= self.end_date):
            raise ValueError(
                "bill_date must lie within start_date and end_date"
                            )
        return self


class BillRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
        )

    public_id: str
    bill_code: str
    bill_date: datetime
    start_date: datetime
    end_date: datetime
    monthly_count: int
    bill_amount: Decimal = Field(examples=[3400, 9332])

    customer_public_id: str

    package_id: IdValueRead
    created_by_id: IdValueRead

    created_at: datetime
    updated_at: datetime


class BillUpdate(BaseModel):

    start_date: Optional[datetime] = Field(
        default=None
        )
    # includes time, validate time as well
    end_date: Optional[datetime] = Field(
        default=None
        )
    monthly_count:  Optional[int] = Field(
        default=None, ge=0, le=12
        )
    bill_amount:  Optional[Decimal] = Field(
        default=None, ge=0
        )
    package_id: Optional[int] = Field(
        default=None
        )

    @model_validator(mode="after")
    def validate_billing_period(self):
        """
        Validation for PATCH semantics:
        - Only validate if both dates are provided
        """

        if self.end_date and self.start_date:
            if self.end_date <= self.start_date:
                raise ValueError(
                    "end_date must be after start_date"
                )
        return self




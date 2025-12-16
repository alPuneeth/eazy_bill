from pydantic import BaseModel, Field, model_validator, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

BillCodeStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=30)
]


class BillCreate(BaseModel):
    bill_code: BillCodeStr
    bill_date: datetime 
    start_date: datetime
    end_date: datetime
    monthly_count: int = Field(default=1, ge=0, le=12)
    bill_amount: float = Field(ge=0)

    customer_id: int
    package_id: int

    @model_validator(mode="after")
    def validate_billing_period(self):
        """
        Ensures the subscription period is logically valid.
        This method runs AFTER all fields are parsed and available.
        """

        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be after start_date"
            )
        return self


class BillRead(BaseModel):
    model_config = {"from_attributes": True}

    public_id: str
    bill_code: str
    bill_date: datetime
    start_date: datetime
    end_date: datetime
    monthly_count: int
    bill_amount: float

    customer_id: int
    package_id: int

    created_at: datetime
    updated_at: datetime


class BillUpdate(BaseModel):
    bill_code: Optional[BillCodeStr] = Field(default=None)
    bill_date: Optional[datetime] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)  # includes time, validate time as well
    end_date: Optional[datetime] = Field(default=None)
    monthly_count:  Optional[int] = Field(default=None, ge=0, le=12)
    bill_amount:  Optional[float] = Field(default=None, ge=0)

    customer_id: Optional[int] = Field(default=None)
    package_id: Optional[int] = Field(default=None)

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




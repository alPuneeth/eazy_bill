from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime


class SubscriptionCreate(BaseModel):
    customer_id: int
    package_id: int

    start_date: datetime = Field(
        title="Start date",
        description="Subscription start date"
    )
    end_date: datetime = Field(
        title="End date",
        description="Subscription end date"
    )

    @model_validator(mode="after")
    def validate_subscription_period(self):
        """
        Ensures the subscription period is logically valid.
        This method runs AFTER all fields are parsed and available.
        """

        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be after start_date"
            )
        return self


class SubscriptionRead(BaseModel):
    model_config = {"from_attributes": True}

    public_id: str
    customer_id: int
    package_id: int
    start_date: datetime
    end_date: datetime

    created_at: datetime
    updated_at: datetime


class SubscriptionUpdate(BaseModel):

    package_id: Optional[int] = Field(
        default=None
        )

    start_date: Optional[datetime] = Field(
        default=None
        )
    end_date: Optional[datetime] = Field(
        default=None
        )

    @model_validator(mode="after")
    def validate_subscription_period(self):
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

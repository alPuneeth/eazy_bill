from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.schemas.common import IdValueRead


class BillFilterRequest(BaseModel):

    from_date: Optional[date] = Field(
        default=None,
        description="Start date (inclusive). Returns bills with bill_date >= this value."
    )

    to_date: Optional[date] = Field(
        default=None,
        description="End date (inclusive). Returns bills with bill_date <= this value."
    )

    village_ids: Optional[List[int]] = Field(
        default=None,
        description=(
            "List of village IDs to filter bills. "
            "Matches bills whose customer belongs to any of these villages. "
            "None or [] = ignore filter"
        )
    )

    ftth64_ids: Optional[List[int]] = Field(
        default=None,
        description=(
            "List of FTTH64 IDs to filter bills. "
            "Matches bills whose customer is assigned to any of these FTTH64 connections. "
            "None or [] = ignore filter"
        )
    )

    agent_ids: Optional[List[int]] = Field(
        default=None,
        description=(
            "List of agent (user) IDs. "
            "Matches bills where the customer's village is assigned to any of these agents. "
            "None or [] = ignore filter"
        )
    )

    @model_validator(mode="after")
    def validate_and_normalize(self):
        # date validation
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date cannot be after to_date")

        # normalize empty lists
        for field in ("village_ids", "ftth64_ids", "agent_ids"):
            if getattr(self, field) == []:
                setattr(self, field, None)

        return self
        
    

class BillFilterRead(BaseModel):
    public_id: str
    bill_code: str
    bill_date: datetime
    start_date: datetime
    end_date: datetime
    monthly_count: int
    bill_amount: Decimal = Field(examples=[3400, 9332])

    customer_public_id: str
    customer_name: str

    package: IdValueRead
    created_by: IdValueRead

    created_at: datetime
    updated_at: datetime

    # village_id: int
    # ftth64_id: Optional[int]
    # agent_id: Optional[int]



class BillFilterResponse(BaseModel):
    data: List[BillFilterRead]
    total_amount: Optional[Decimal] = None
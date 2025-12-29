from pydantic import BaseModel, Field
from decimal import Decimal


class CollectionsSummaryRead(BaseModel):
    today_collection: Decimal = Field(
        description="Total bill amount collected today"
    )
    monthly_collection: Decimal = Field(
        description="Total bill amount collected in the current month"
    )

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.lookup.customer_type import CustomerTypeEnum


class CustomerTypeCreate(BaseModel):
    name: CustomerTypeEnum = Field(
        title="Customer Type",
        description="Classification of the customer",
        json_schema_extra={
            "examples": ["regular", "sponsored"]
            }
        )

    description: Optional[str] = Field(
        default=None
        )


class CustomerTypeRead(BaseModel):
    model_config = {
        "from_attributes": True
        }
    id: int
    public_id: str
    name: CustomerTypeEnum

    description: Optional[str] = Field(
        default=None
        )

    created_at: datetime
    updated_at: datetime


class CustomerTypeUpdate(BaseModel):
    name: Optional[CustomerTypeEnum] = Field(
        default=None
        )
    description: Optional[str] = Field(
        default=None
        )

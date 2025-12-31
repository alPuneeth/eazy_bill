from pydantic import BaseModel
from app.schemas.customers.customer_onboard import (
    CustomerOnboardCreate,
    CustomerOnboardRead
    )


class CustomerOnboardBulkCreate(BaseModel):
    customers: list[CustomerOnboardCreate]


class CustomerOnboardBulkFailure(BaseModel):
    index: int
    name: str
    phone: str
    reason: str


class CustomerOnboardBulkRead(BaseModel):
    success: list[CustomerOnboardRead]
    failed: list[CustomerOnboardBulkFailure]

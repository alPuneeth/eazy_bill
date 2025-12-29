from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class BillByAgentRead(BaseModel):
    bill_public_id: str
    bill_code: str
    bill_date: datetime
    start_date: datetime
    end_date: datetime
    monthly_count: int
    bill_amount: Decimal

    customer_public_id: str
    customer_name: str

    package_name: str

    agent_public_id: str
    agent_name: str

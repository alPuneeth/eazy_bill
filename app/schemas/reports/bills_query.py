from pydantic import BaseModel, ConfigDict
from sqlmodel import Field
from decimal import Decimal
from datetime import datetime

from app.schemas.common import IdValueRead


class BillReportRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid"
    )
    # ── Customer ──
    customer_public_id: str
    customer_name: str

    # ── Bill core ──
    public_id: str
    bill_code: str
    bill_date: datetime
    start_date: datetime
    end_date: datetime
    bill_amount: Decimal

    # ── Village ──
    village_name: str 

    # ── Connection ──
    vc_number: str     
    ftth64_name: str

    # ── Package ──
    package: IdValueRead

    # ── Audit ──
    created_by: IdValueRead
    created_at: datetime
    updated_at: datetime
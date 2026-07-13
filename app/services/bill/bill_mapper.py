from app.schemas.bill import BillRead
from app.schemas.common import IdValueRead, CreatorSummary

def map_bill_row(r) -> BillRead:
    return BillRead(
        public_id=r["public_id"],
        bill_code=r["bill_code"],
        bill_date=r["bill_date"],
        start_date=r["start_date"],
        end_date=r["end_date"],
        monthly_count=r["monthly_count"],
        bill_amount=r["bill_amount"],
        customer_public_id=r["customer_public_id"],
        package_id=IdValueRead(
            id=r["package_id"],
            value=r["package_value"]
        ),
        created_by_id=CreatorSummary(
            public_id=r["created_by_public_id"],
            name=r["created_by_name"]
        ),
        created_at=r["created_at"],
        updated_at=r["updated_at"],
    )
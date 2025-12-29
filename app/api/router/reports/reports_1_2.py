from fastapi import APIRouter, Depends
from sqlmodel import select, Session

from app.services.reports.customer_status_summary_vil import (
    get_customer_status_summary
)
from app.schemas.reports.customer_status_summary_vil import (
    VillageCustomerStatusSummary
)
from app.db.session import get_session
from app.dependencies.auth import get_current_user
from app.models.core_models.user import User
from app.schemas.bill import BillRead
from app.services.reports.get_customer_bills import (
    get_customer_bills_all_time
)


router = APIRouter(
    prefix=("/reports"),
    tags=["Reports"]
)

# Report_1: Customer count by village
@router.get(
    "/customer_status_summary_by_village",
    response_model=list[VillageCustomerStatusSummary]
)
def customer_status_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return get_customer_status_summary(
        session=session,
        current_user=current_user
    )


# Report_2: Customer bills of all time
@router.get(
    "/customer-bills/{customer_public_id}",
    response_model=list[BillRead]
)
def get_customer_bills(
    customer_public_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return get_customer_bills_all_time(
        session=session,
        customer_public_id=customer_public_id,
        current_user=current_user
    )

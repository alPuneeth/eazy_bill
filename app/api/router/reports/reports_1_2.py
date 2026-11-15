from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.services.reports.customer_status_summary_vil import (
    get_customer_status_summary
)
from app.schemas.reports.customer_status_summary_vil import (
    VillageCustomerStatusSummary
)
from app.db.session import get_session
from app.dependencies.auth import get_current_user
from app.models.core_models.user import User


router = APIRouter(
    prefix=("/reports"),
    tags=["Reports"]
)

# Report_1: Customer count by village
@router.get(
    "/customer-status-summary-by-village",
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


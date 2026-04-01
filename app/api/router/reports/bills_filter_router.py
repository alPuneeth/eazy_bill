from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.dependencies.auth import get_current_user
from app.models.core_models.user import User
from app.schemas.reports.bills_by_optional_filters import (
    BillFilterRequest, BillFilterResponse)
from app.services.reports.bills_by_optional_filter import bill_op_filters


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post("/bills_with_optional_filters/",
            response_model=BillFilterResponse,
            dependencies=[]
            )
def get_bills_with_op_filters(filters: BillFilterRequest,
                              session: Session = Depends(get_session),
                              current_user: User = Depends(get_current_user)
                              ):

    return bill_op_filters( filters, current_user, session)
from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db.session import get_session
from app.dependencies.auth import get_current_user
from app.models.core_models.user import User
from app.schemas.reports.bills_query import BillReportRead
from app.services.reports.query_bills import get_bills_with_filters


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get(
    "/bills_with_filters",
    response_model=list[BillReportRead],
    summary="Get bills report with optional filters"
)
def get_bills_report(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),

    # ── Optional date filters ──
    from_date: Optional[date] = Query(
        default=None,
        description="Include bills from this date (inclusive)"
    ),
    to_date: Optional[date] = Query(
        default=None,
        description="Include bills up to this date (inclusive)"
    ),

    # ── Optional village filters ──
    village_ids: Optional[List[int]] = Query(
        default=None,
        description="Filter by one or more village IDs"
    ),

    # ── Optional FTTH64 filter ──
    ftth64_id: Annotated[
        int, Query(
        description="Filter by FTTH64 ID")
        ] = None
):
    """
    Bill report endpoint.

    - All filters are optional
    - Date filters are inclusive
    - RBAC is enforced automatically
    - Returns bill-level rows enriched with business context
    """

    return get_bills_with_filters(
        session=session,
        current_user=current_user,
        from_date=from_date,
        to_date=to_date,
        village_ids=village_ids,
        ftth64_id=ftth64_id,
    )

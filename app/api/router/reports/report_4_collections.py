from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.services.reports.collections_summary import get_collections_summary
from app.schemas.reports.collections import CollectionsSummaryRead


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get(
    "/collections_summary",
    response_model=CollectionsSummaryRead
)
def collections_summary(
    session: Session = Depends(get_session)
):
    return get_collections_summary(session)

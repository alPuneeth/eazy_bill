from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.models.core_models.user import User
from app.services.reports.collections_summary import get_collections_summary
from app.schemas.reports.collections import CollectionsSummaryRead
from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get(
    "/collections_summary",
    response_model=CollectionsSummaryRead
)
def collections_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return get_collections_summary(session=session, current_user=current_user)

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.dependencies.rbac import require_admin
from app.schemas.reports.bill_by_agent import BillByAgentRead
from app.services.reports.bills_by_agent import (
    get_bills_created_by_agent
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(require_admin)]
)


@router.get(
    "/bills_by_agent/{agent_public_id}",
    response_model=list[BillByAgentRead]
)
def bills_by_agent(
    agent_public_id: str,
    session: Session = Depends(get_session)
):
    return get_bills_created_by_agent(
        agent_public_id=agent_public_id,
        session=session
    )

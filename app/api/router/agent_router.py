from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.schemas.village import VillageRead, AssignVillagesRequest
from app.services.agent_service import assign_villages_to_agent_service

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
    )


@router.post("/{agent_public_id}/villages",
             response_model=list[VillageRead],
             dependencies=[Depends(require_admin)])
def assign_villages_to_agent(
    agent_public_id: str,
    payload: AssignVillagesRequest,
    session: Session = Depends(get_session)
):
    return assign_villages_to_agent_service(
        session,
        agent_public_id,
        payload.village_ids,
        payload.force
    )

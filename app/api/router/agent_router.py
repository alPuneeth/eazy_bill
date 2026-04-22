import logging
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.schemas.village import AssignVillagesResponse, VillageRead, AssignVillagesRequest, ReplaceVillagesRequest
from app.services.agent_service import assign_villages_to_agent_service, replace_villages_to_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
    )


@router.post("/{agent_public_id}/villages",
             response_model=AssignVillagesResponse,
             dependencies=[Depends(require_admin)],
             summary="Assign villages to an agent",
    description=(
        "Assigns the given villages to the agent (additive operation). "
        "Existing assignments are preserved. "
        "If a village is already assigned to another agent, the request will fail "
        "unless force=true is provided, in which case ownership is reassigned."
    ))
def assign_villages_to_agent(
    agent_public_id: str,
    payload: AssignVillagesRequest,
    session: Session = Depends(get_session)
):
    logger.info(
        f"Assign villages - start | agent_id={agent_public_id}"
    )

    try:
        result = assign_villages_to_agent_service(
        session,
        agent_public_id,
        payload.village_ids,
        payload.force
    )

        logger.info(
            f"Assign villages - success | agent_id={agent_public_id}"
        )

        return result

    except Exception:
        logger.exception(
            f"Assign villages - failed | agent_id={agent_public_id}"
        )
        raise


@router.put("/{agent_public_id}/villages",
            response_model=list[VillageRead],
            dependencies=[Depends(require_admin)],
            summary="Replace villages of an agent",
    description="Replaces all existing village assignments of the agent with " \
    "the provided list. Previous assignments will be removed."
            )
def replace_villages_for_agent(
    agent_public_id: str,
    payload: ReplaceVillagesRequest,
    session: Session = Depends(get_session)
):
    logger.info(
        f"Replace villages - start | agent_id={agent_public_id}"
    )
    try:
        result = replace_villages_to_agent_service(
            session,
            agent_public_id,
            payload.village_ids
        )
        logger.info(
             f"Replace villages - success | agent_id={agent_public_id} "
        )
        return result
    
    except Exception:
        logger.exception(
            f"Replace villages - failed | agent_id={agent_public_id}"
        )
        raise
        
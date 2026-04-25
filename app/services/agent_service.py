import logging
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village
from app.schemas.village import AssignVillagesResponse, VillageRead

logger = logging.getLogger(__name__)


def assign_villages_to_agent_service(
    session: Session,
    agent_public_id: str,
    village_ids: list[int],
    force: bool = False
):
    """
    Assign villages to a specific agent.

    This performs an additive assignment. Existing assignments are preserved
    unless overridden using the `force` flag.

    Behavior:
        - Unassigned villages are assigned to the agent.
        - Villages already assigned to the same agent are skipped.
        - Villages assigned to another agent:
            * force=False → raises HTTP 400
            * force=True  → reassigns ownership

    The operation is atomic. If a conflict occurs with force=False,
    no changes are committed.

    Args:
        session (Session): Database session.
        agent_public_id (str): Public identifier of the agent.
        village_ids (list[int]): List of village IDs to assign.
        force (bool, optional): Override existing ownership. Defaults to False.

    Returns:
        AssignVillagesResponse: Contains assigned villages and already assigned IDs.

    Raises:
        HTTPException:
            404: Agent or villages not found.
            400: Conflict when force=False.
            409: Database integrity failure.
    """
    village_ids = list(set(village_ids)) 

    try:
        # 1. Fetch + validate agent
        agent = session.exec(
            select(User).where(User.public_id == agent_public_id)
        ).first()

        if not agent:
            raise HTTPException(404, "Agent not found")

        if agent.role != UserRole.AGENT:
            raise HTTPException(400, "User is not an agent")

        # 2. Fetch villages (NO relationship load here)
        villages = session.exec(
            select(Village).where(Village.id.in_(village_ids))
        ).all()

        requested_ids = set(village_ids)
        found_ids = {v.id for v in villages}
        missing_ids = requested_ids - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Villages not found: {list(missing_ids)}"
            )

        if not villages:
            raise HTTPException(404, "No villages found")
        
        already_assigned_ids = []

        # 3. Assign correctly
        for v in villages:
            if v.agent_id is None:
                continue

            elif v.agent_id == agent.id:
                already_assigned_ids.append(v.id)

            else:
                if not force:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Village {v.id} already assigned to another agent"
                    )
                logger.info(f"Force reassignment applied | village_id={v.id}")
                
        for v in villages:
            if v.agent_id != agent.id:
                v.agent_id = agent.id

        session.commit()


    except IntegrityError:
        session.rollback()
        logger.exception("DB commit failed - assign villages")
        raise HTTPException(409, "Assignment failed")

    except Exception:
        logger.exception(
            "Unexpected failure - assign villages"
                         )
        raise

    # 5. Re-fetch with relationship
    villages = session.exec(
        select(Village)
        .options(selectinload(Village.agent))
        .where(Village.id.in_(village_ids))
    ).all()

    # 6. Return mapped response
    return AssignVillagesResponse(
        assigned=[
            VillageRead(
            id=v.id,
            name=v.name,
            postal_code=v.postal_code,
            village_code=v.village_code,
            agent_public_id=v.agent.public_id if v.agent else None,
            created_at=v.created_at,
            updated_at=v.updated_at
        )
        for v in villages if v.id not in already_assigned_ids
        ],
        already_assigned=already_assigned_ids
        )
    


def replace_villages_to_agent_service(
        session: Session,
        agent_public_id: str,
        village_ids: list[int]
):
    """
    Replace all village assignments for a given agent.

    This service performs a full replacement of villages assigned to an agent.
    Existing assignments are removed and replaced with the provided list.

    Behavior:
        - If `village_ids` is empty:
            • All currently assigned villages are unassigned
        - If `village_ids` is provided:
            • Villages currently assigned but not in the new list are unassigned
            • Villages in the new list are assigned to the agent
            • Overlapping villages remain unchanged

    The operation is atomic:
        - All changes are committed together
        - On failure, no partial updates are persisted

    Parameters:
        - session (Session): Database session
        - agent_public_id (str): Public identifier of the target agent
        - village_ids (list[int]): Final set of village IDs to assign

    Returns:
        - list[VillageRead]:
            Updated list of villages assigned to the agent after replacement

    Raises:
        - HTTPException:
            • 404 → Agent not found or any village ID is invalid
            • 400 → User is not an agent
            • 409 → Database integrity failure during commit
    """
    village_ids = list(set(village_ids))

    try:

        # 1. Fetch + validate agent
        agent = session.exec(
            select(User).where(User.public_id == agent_public_id)
        ).first()

        if not agent:
            raise HTTPException(404, "Agent not found")

        if agent.role != UserRole.AGENT:
            raise HTTPException(400, "User is not an agent")
        
        if not village_ids:
            # remove all villages from agent
            current_villages = session.exec(
                select(Village).where(Village.agent_id == agent.id)
            ).all()

            for v in current_villages:
                v.agent_id = None
            
            logger.info(f"Replace villages - clearing all | agent_id={agent_public_id}")
            
            session.commit()
            return []


        # 2. Fetch villages (NO relationship load here)
        villages = session.exec(
            select(Village).where(Village.id.in_(village_ids))
        ).all()

        requested_ids = set(village_ids)
        found_ids = {v.id for v in villages}

        missing_ids = requested_ids - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Villages not found: {list(missing_ids)}"
            )
        
        # 3. fetch current assignments
        current_villages = session.exec(
            select(Village).where(Village.agent_id == agent.id)
        ).all()

        current_ids = {v.id for v in current_villages}
        new_ids = set(village_ids)

        # 4. compute diff
        ids_to_remove = current_ids - new_ids   # villages to unassign
        to_add_ids = new_ids - current_ids      # villages to assign 

        logger.info(
                f"Village replacement diff | remove={len(ids_to_remove)} | add={len(to_add_ids)}"
            )
        
        # conflict check BEFORE any mutation
        for v in villages:
            if v.agent_id is not None and v.agent_id != agent.id:
                raise HTTPException(
                        status_code=400,
                        detail=f"Village {v.id} already assigned to another agent"
                    )

        # 5. unassign 
        for v in current_villages:
            if v.id in ids_to_remove:
                v.agent_id = None

        # 6. Assign new villages
        for v in villages:
            if v.agent_id != agent.id:
                v.agent_id = agent.id

        session.commit()

    except IntegrityError:
        session.rollback()
        logger.exception("DB commit failed - replace villages")
        raise HTTPException(409, "Replacement failed")

    except Exception:
        logger.exception(
            "Unexpected failure - replace villages"
                         )
        raise

    # 8. Re-fetch with relationship
    villages = session.exec(
        select(Village)
        .options(selectinload(Village.agent))
        .where(Village.id.in_(village_ids))
    ).all()

    # 9. Return mapped response
    return [
        VillageRead(
            id=v.id,
            name=v.name,
            postal_code=v.postal_code,
            village_code=v.village_code,
            agent_public_id=v.agent.public_id if v.agent else None,
            created_at=v.created_at,
            updated_at=v.updated_at
        )
        for v in villages
    ]
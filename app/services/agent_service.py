from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village
from app.schemas.village import VillageRead


def assign_villages_to_agent_service(
    session: Session,
    agent_public_id: str,
    village_ids: list[int],
    force: bool = False
):
    village_ids = list(set(village_ids))

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

    # 3. Assign correctly
    for v in villages:
        if v.agent_id is None:
            v.agent_id = agent.id

        elif v.agent_id == agent.id:
            continue

        else:
            if not force:
                raise HTTPException(
                    status_code=400,
                    detail=f"Village {v.id} already assigned to another agent"
                )
            v.agent_id = agent.id

    # 4. Commit
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "Assignment failed")

    # 5. Re-fetch with relationship
    villages = session.exec(
        select(Village)
        .options(selectinload(Village.agent))
        .where(Village.id.in_(village_ids))
    ).all()

    # 6. Return mapped response
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

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload


from app.dependencies.rbac import require_admin
from app.models.core_models.user import UserRole
from app.services.village_mapper import to_village_read
from app.db.session import get_session
from app.models.core_models.user import User
from app.dependencies.auth import get_current_user
from app.models.lookup.village import Village
from app.schemas.lookup.village import (
    VillageCreate,
    VillageRead,
    VillageUpdate
)

router = APIRouter(
    prefix="/village",
    tags=["Village"],
    dependencies=[Depends(get_current_user)]
    )


@router.get("/", response_model=list[VillageRead])
def list_villages(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Village).options(joinedload(Village.agent))

    # RBAC Filter
    if current_user.role == UserRole.AGENT:
        stmt = stmt.where(Village.agent_id == current_user.id)

    villages = session.exec(stmt).all()

    return [
        to_village_read(v)
        for v in villages
    ]   


@router.get("/{village_id}", response_model=VillageRead)
def get_village(
    village_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement =  select(Village).options(joinedload(Village.agent))

    # RBAC Filter
    if current_user.role == UserRole.AGENT:
        statement = statement.where(Village.agent_id == current_user.id)

    village = session.exec(
        statement.where(Village.id == village_id)
    ).first()

    if not village:
        raise HTTPException(status_code=404, detail="Village not found")


    return to_village_read(village)


@router.post("/", response_model=VillageRead,
             dependencies=[Depends(require_admin)])
def create_village(
    payload: VillageCreate,
    session: Session = Depends(get_session)
                        ):
    village = Village.model_validate(payload)
    session.add(village)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Village with this name already exists"
             )

     # 🔑 reload with relationship
    village = session.exec(
        select(Village)
        .options(joinedload(Village.agent))
        .where(Village.id == village.id)
    ).first()

    return to_village_read(village)


@router.patch("/{village_id}", response_model=VillageRead,
              dependencies=[Depends(require_admin)])
def update_village(
    village_id: int,
    payload: VillageUpdate,
    session: Session = Depends(get_session)
):
    village = session.exec(
    select(Village)
    .options(joinedload(Village.agent))
    .where(Village.id == village_id)
).first()

    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    update_data = payload.model_dump(exclude_unset=True)
    village.sqlmodel_update(update_data)

    try:
        session.commit()
    
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Village with this name already exists"
        )
     # 🔑 reload again (important after update)
    village = session.exec(
        select(Village)
        .options(joinedload(Village.agent))
        .where(Village.id == village_id)
    ).first()

    return to_village_read(village)
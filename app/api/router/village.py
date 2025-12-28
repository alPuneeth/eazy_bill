from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.models.core_models.user import User
from app.dependencies.auth import get_current_user
from app.models.lookup.village import Village
from app.schemas.village import (
    VillageCreate,
    VillageRead,
    VillageUpdate
)

router = APIRouter(
    prefix="/village",
    tags=["Village"]
    )


@router.get("/", response_model=list[VillageRead])
def list_villages(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Village)

    # restrict for agents (and any non-admin)
    if current_user.role != "admin":
        stmt = stmt.where(Village.agent_restricted.is_(False))

    return session.exec(stmt).all()


@router.get("/{village_id}", response_model=VillageRead)
def get_village(
    village_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    village = session.get(Village, village_id)
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    if current_user.role != "admin" and village.agent_restricted:
        raise HTTPException(
            status_code=403,
            detail="Access to this village is restricted"
        )
    return village


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

    session.refresh(village)
    return village


@router.patch("/{village_id}", response_model=VillageRead,
              dependencies=[Depends(require_admin)])
def update_village(
    village_id: int,
    payload: VillageUpdate,
    session: Session = Depends(get_session)
):
    village = session.get(Village, village_id)
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(village, key, value)

    session.commit()
    session.refresh(village)
    return village
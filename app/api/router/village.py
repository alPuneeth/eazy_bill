from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.models.lookup.village import Village
from app.schemas.village import (
    VillageCreate,
    VillageRead,
    VillageUpdate
)

router = APIRouter(
    prefix="/village",
    tags=["Village"],
    dependencies=[Depends(require_admin)]
    )


@router.get("/", response_model=list[VillageRead])
def list_villages(
    session: Session = Depends(get_session)
):
    villages = session.exec(select(Village)).all()
    return villages


@router.get("/{village_id}", response_model=VillageRead)
def get_village(
    village_id: int,
    session: Session = Depends(get_session)
):
    village = session.get(Village, village_id)
    if not village:
        raise HTTPException(status_code=404, detail="Village not found")
    return village


@router.post("/", response_model=VillageRead)
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


@router.patch("/{village_id}", response_model=VillageRead)
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
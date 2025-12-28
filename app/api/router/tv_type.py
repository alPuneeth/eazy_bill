from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.models.lookup.tv_type import TVType
from app.schemas.lookup.tv_type import (
    TVTypeCreate,
    TVTypeRead,
    TVTypeUpdate
)

router = APIRouter(
    prefix="/tv_type",
    tags=["TVType"]
    )


@router.get("/", response_model=list[TVTypeRead])
def list_tv_types(
    session: Session = Depends(get_session)
):
    tv_types = session.exec(select(TVType)).all()
    return tv_types


@router.get("/{tv_type_id}", response_model=TVTypeRead)
def get_tv_type(
    tv_type_id: int,
    session: Session = Depends(get_session)
):
    tv_type = session.get(TVType, tv_type_id)
    if not tv_type:
        raise HTTPException(status_code=404, detail="TVType not found")
    return tv_type


@router.post("/", response_model=TVTypeRead,
             dependencies=[Depends(require_admin)])
def create_tv_type(
    payload: TVTypeCreate,
    session: Session = Depends(get_session)
                        ):
    tv_type = TVType.model_validate(payload)
    session.add(tv_type)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="TVType with this name already exists"
             )

    session.refresh(tv_type)
    return tv_type


@router.patch("/{tv_type_id}", response_model=TVTypeRead,
              dependencies=[Depends(require_admin)])
def update_tv_type(
    tv_type_id: int,
    payload: TVTypeUpdate,
    session: Session = Depends(get_session)
):
    tv_type = session.get(TVType, tv_type_id)
    if not tv_type:
        raise HTTPException(status_code=404, detail="TVType not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tv_type, key, value)

    session.commit()
    session.refresh(tv_type)
    return tv_type
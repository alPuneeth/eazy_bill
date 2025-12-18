from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.db.session import get_session
from app.models.lookup.status import Status
from app.schemas.lookup.status import (
    StatusCreate,
    StatusRead,
    StatusUpdate
)

router = APIRouter(
    prefix="/status",
    tags=["Status"]
    )


@router.post("/", response_model=StatusRead)
def create_status(
    payload: StatusCreate,
    session: Session = Depends(get_session)
                        ):
    status = Status.model_validate(payload)
    session.add(status)

    try:
        session.commit()
    
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Status with this name already exists"
             )
    
    session.refresh(status)
    return status


@router.get("/{status_id}", response_model=StatusRead)
def get_status(
    status_id: int,
    session: Session = Depends(get_session)
):
    status = session.get(Status, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status


@router.get("/", response_model=list[StatusRead])
def list_statuses(
    session: Session = Depends(get_session)
):
    statuses = session.exec(select(Status)).all()
    return statuses


@router.patch("/{status_id}", response_model=StatusRead)
def update_status(
    status_id: int,
    payload: StatusUpdate,
    session: Session = Depends(get_session)
):
    status = session.get(Status, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(status, key, value)

    session.commit()
    session.refresh(status)
    return status
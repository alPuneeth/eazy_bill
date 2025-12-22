from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.models.lookup.ftth64 import FTTH64
from app.schemas.lookup.ftth64 import (
    FTTH64Create,
    FTTH64Read,
    FTTH64Update
)

router = APIRouter(
    prefix="/ftth64",
    tags=["FTTH64"],
    dependencies=[Depends(require_admin)]
    )


@router.get("/", response_model=list[FTTH64Read])
def list_ftth64(
    session: Session = Depends(get_session)
):
    ftth64 = session.exec(select(FTTH64)).all()
    return ftth64


@router.get("/{ftth64_id}", response_model=FTTH64Read)
def get_ftth64(
    ftth64_id: int,
    session: Session = Depends(get_session)
):
    ftth64 = session.get(FTTH64, ftth64_id)
    if not ftth64:
        raise HTTPException(status_code=404, detail="FTTH64 not found")
    return ftth64


@router.post("/", response_model=FTTH64Read)
def create_ftth64(
    payload: FTTH64Create,
    session: Session = Depends(get_session)
                        ):
    ftth64 = FTTH64.model_validate(payload)
    session.add(ftth64)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="FTTH64 with this name already exists"
             )

    session.refresh(ftth64)
    return ftth64


@router.patch("/{ftth64_id}", response_model=FTTH64Read)
def update_ftth64(
    ftth64_id: int,
    payload: FTTH64Update,
    session: Session = Depends(get_session)
):
    ftth64 = session.get(FTTH64, ftth64_id)
    if not ftth64:
        raise HTTPException(status_code=404, detail="FTTH64 not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ftth64, key, value)

    session.commit()
    session.refresh(ftth64)
    return ftth64
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError


from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_admin
from app.db.session import get_session
from app.models.core_models.user import User
from app.models.lookup.ftth64 import FTTH64
from app.schemas.lookup.ftth64 import (
    FTTH64Create,
    FTTH64Read,
    FTTH64Update
)

router = APIRouter(
    prefix="/ftth64",
    tags=["FTTH64"],
    dependencies=[Depends(get_current_user)]
    )


@router.get("/", response_model=list[FTTH64Read])
def list_ftth64(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
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


@router.post("/", response_model=FTTH64Read,
             dependencies=[Depends(require_admin)])
def create_ftth64(
    payload: FTTH64Create,
    session: Session = Depends(get_session)
                        ):
    
    existing_ftth64 = session.exec(
        select(FTTH64).where(FTTH64.name == payload.name)
    ).first()

    if existing_ftth64:
        raise HTTPException(
            status_code=409,
            detail=f"{payload.name} name already exists"
        )

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


@router.patch("/{ftth64_id}", response_model=FTTH64Read,
              dependencies=[Depends(require_admin)])
def update_ftth64(
    ftth64_id: int,
    payload: FTTH64Update,
    session: Session = Depends(get_session)
):
    ftth64 = session.get(FTTH64, ftth64_id)
    if not ftth64:
        raise HTTPException(status_code=404, detail="FTTH64 not found")
    
    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_ftth64 = session.exec(
        select(FTTH64).where(FTTH64.name == update_data["name"],
                            FTTH64.id != ftth64_id
                            )
        ).first()

        if existing_ftth64:
            raise HTTPException(
            status_code=409,
            detail=f"FTTH64 with name {payload.name} already exists"
             )

    for key, value in update_data.items():
        setattr(ftth64, key, value)

    session.commit()
    session.refresh(ftth64)
    return ftth64
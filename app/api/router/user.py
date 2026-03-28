from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.dependencies.auth import get_current_user
from app.models.lookup.village import Village
from app.services.user_village_mapper import to_user_read
from app.services.enforce_single_admin import enforce_single_admin
from app.dependencies.rbac import require_admin
from app.core.security import get_password_hash
from app.db.session import get_session
from app.models.core_models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserRead
)

router = APIRouter(
    prefix="/user",
    tags=["User"]
    )


@router.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserRead],
            dependencies=[Depends(require_admin)])
def list_users(
    session: Session = Depends(get_session)
):
    stmt = select(User).options(selectinload(User.villages).selectinload(Village.agent))
    users = session.exec(stmt).all()

    return [to_user_read(user) for user in users]


@router.get("/{user_public_id}", response_model=UserRead,
            dependencies=[Depends(require_admin)])
def get_user(
    user_public_id: str,
    session: Session = Depends(get_session)
):
    stmt = select(User).where(User.public_id == user_public_id).options(selectinload(User.villages).selectinload(Village.agent))
    user = session.exec(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserRead,
             dependencies=[Depends(require_admin)])
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session)
                        ):
    if payload.role == UserRole.ADMIN:
        enforce_single_admin(session)

    user = User(
        name=payload.name,
        phone=payload.phone,
        role=payload.role,
        hashed_password=get_password_hash(payload.password)
    )

    session.add(user)

    try:
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Invalid reference or duplicate User data"
        )
    session.refresh(user)
    return user

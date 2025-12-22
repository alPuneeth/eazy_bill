from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_admin
from app.core.security import get_password_hash
from app.db.session import get_session
from app.models.core_models.user import User
from app.schemas.user import (
    UserCreate,
    UserRead
)

router = APIRouter(
    prefix="/user",
    tags=["User"],
    dependencies=[Depends(require_admin)]
    )


@router.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session)
):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_public_id}", response_model=UserRead)
def get_user(
    user_public_id: str,
    session: Session = Depends(get_session)
):
    user = session.exec(
        select(User).where(User.public_id == user_public_id)
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserRead)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session)
                        ):
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
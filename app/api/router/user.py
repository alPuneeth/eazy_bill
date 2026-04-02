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
    UserRead,
    UserUpdate
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


@router.post("/create", response_model=UserRead,
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
        user_code=payload.user_code, 
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


@router.patch("/update/{user_public_id}",
              response_model=UserRead,
              dependencies=[Depends(require_admin)])
def update_user(
    user_public_id: str,
    payload: UserUpdate,
    session: Session = Depends(get_session),
):
    user = session.exec(
        select(User).where(User.public_id == user_public_id)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )
    # --- enforce role rules ---
    # if user.role == UserRole.ADMIN:
    #     update_data["user_code"] = "KVR"
    if "user_code" in update_data and user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="user_code cannot be modified for this role"
        )

    elif user.role == UserRole.TEST_USER:
        if "user_code" in update_data:
            update_data["user_code"] = "TST"

    elif user.role == UserRole.AGENT:
        if ("user_code" not in update_data or not update_data["user_code"]):
            raise HTTPException(
                status_code=400,
                detail="user_code is required for AGENT"
        )
        update_data["user_code"] = update_data["user_code"].upper()

    user.sqlmodel_update(update_data)
    # better alternative to the following:
    # for key, value in update_data.items():
    #    setattr(user, key, value)
    
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    
    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=409,
            detail="Constraint violation"
            )
    
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Unexpected database error")
    
    return user



from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.core_models.user import User, UserRole


def enforce_single_admin(session: Session):
    """
    objective of this function:
    When creating and updating a new user with a user role "ADMIN", first we need to check if any user 
    with the admin role exists. If yes, raise HTTPException(status_code=409, detail="ADMIN already exists!")
    """
    existing_admin = session.exec(
        select(User).where(User.role == UserRole.ADMIN)
    ).first()

    if existing_admin:
        raise HTTPException(
            status_code=409,
            detail="ADMIN already exists!"
        )

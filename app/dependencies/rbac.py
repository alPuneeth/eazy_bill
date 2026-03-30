from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional

from app.dependencies.auth import get_current_user_optional, get_current_user
from app.db.session import get_session
from app.models.core_models.user import User


# test_user exists
def require_admin(
        session: Session = Depends(get_session),
        current_user: Optional[User] = Depends(get_current_user_optional)
):
    admin_exists = session.exec(
        select(User).where(User.role == "admin")
    ).first()

    # no admin exists, allow request without token
    if not admin_exists:   # BOOTSTRAP mode
        return None

    if not current_user or current_user.role not in ("admin", "test_user"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


# test_user exists
def require_admin_or_agent(
        current_user=Depends(get_current_user)
):
    if current_user.role not in ("admin", "agent", "test_user"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return current_user
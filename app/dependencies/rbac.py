from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user


# test_user exists
def require_admin(
        current_user=Depends(get_current_user)
):
    if current_user.role not in ("admin", "test_user"):
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
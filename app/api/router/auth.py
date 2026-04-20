from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.db.session import get_session
from app.models.core_models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate a user and issue an access token.
    """

    # 1. Fetch user by Username
    user = session.exec(
        select(User).where(User.phone == payload.phone)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # 2. Verify password
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Inactive user"
        )

    # 3. Update last login (only on SUCCESS)
    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)   # optional but explicit
    session.commit()    # persist change
    session.refresh(user)  # ensures updated value is in memory

    # 4. JWT
    access_token = create_access_token(
        data={"sub": user.public_id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

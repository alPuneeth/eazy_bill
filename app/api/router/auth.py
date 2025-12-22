from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

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
    Authenticate a usr and issue an access token.
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

    # 3. JWT
    access_token = create_access_token(
        data={"sub": user.public_id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

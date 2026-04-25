import logging
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.db.session import get_session
from app.models.core_models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token

logger = logging.getLogger(__name__)
 
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
    logger.info(
        "Login - start | phone=%s",
        payload.phone[-4:].rjust(len(payload.phone), "*")
        )

    try:
        # 1. Fetch user by Username
        user = session.exec(
            select(User).where(User.phone == payload.phone)
        ).first()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Inactive user"
            )
        
        # 2. Update last login (only on SUCCESS)
        user.last_login_at = datetime.now(timezone.utc)
        session.add(user)   # optional but explicit
        session.commit()    # persist change
        session.refresh(user)  # ensures updated value is in memory

        # 3. JWT
        access_token = create_access_token(
            data={"sub": user.public_id}
        )

        logger.info(f"Login - success | user_id={user.public_id}")

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except HTTPException:
        raise

    except Exception:
        session.rollback()
        logger.exception(f"DB commit failed - login")
        raise

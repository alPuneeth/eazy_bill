from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional

from app.db.session import get_session
from app.auth.jw import SECRET_KEY, ALGORITHM
from app.models.core_models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=[ALGORITHM]
                             )
        user_public_id: str | None = payload.get("sub")
        if user_public_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = session.exec(
        select(User).where(User.public_id == user_public_id)
    ).first()

    if user is None:
        raise credentials_exception

    return user


def get_current_user_optional(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_session)
) -> Optional[User]:

    try:
        if credentials is None:
            return None

        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_public_id = payload.get("sub")

        if not user_public_id:
            return None
        return session.exec(
            select(User).where(User.public_id == user_public_id)
        ).first()
    
    except Exception:
        return None

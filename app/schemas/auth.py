from pydantic import BaseModel
from app.schemas.user import PhoneStr


class LoginRequest(BaseModel):
    """
    Payload sent by client during login.
    """
    phone: PhoneStr
    password: str


class TokenResponse(BaseModel):
    """
    Response returned after successful authentication.
    """
    access_token: str
    token_type: str = "bearer"
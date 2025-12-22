from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    Payload sent by client during login.
    """
    phone: str
    password: str


class TokenResponse(BaseModel):
    """
    Response returned after successful authentication.
    """
    access_token: str
    token_type: str = "bearer"
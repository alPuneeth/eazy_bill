from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

from app.models.core_models.user import UserRole


NonEmptyStr = Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    min_length=1,
                    max_length=30
                    )
                ]

PhoneStr = Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    min_length=8,
                    max_length=15
                    )
                ]


class UserCreate(BaseModel):
    name: NonEmptyStr = Field(
        title="User Name",
        description="Display name of the User"
                       )
    phone: PhoneStr = Field(
        description="Phone number of the user"
    )
    hashed_password: str
    role: UserRole = Field(
        title="User Role",
        description="system role assigned to the user",
        json_schema_extra={
            "examples": ["ADMIN", "AGENT"]
        }
                       )


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    public_id: str

    name: str
    phone: str
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]

    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: Optional[NonEmptyStr] = Field(
        default=None
        )
    phone: Optional[PhoneStr] = Field(
        default=None
        )
    role: Optional[UserRole] = Field(
        default=None
        )
    is_active: Optional[bool] = Field(
        default=None
        )
    last_login_at: Optional[datetime] = Field(
        default=None
        )

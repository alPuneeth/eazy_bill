from pydantic import BaseModel, Field, StringConstraints, model_validator
from typing import Optional, Annotated
from datetime import datetime

from app.models.core_models.user import UserRole
from app.schemas.village import VillageRead


NonEmptyStr = Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    min_length=1,
                    max_length=100
                    )
                ]

PhoneStr = Annotated[
                str,
                StringConstraints(
                    strip_whitespace=True,
                    pattern=r"^\d{10,15}$"
                    )
                ]

UserCodeStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=3
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
    password: str = Field(
        min_length=6,
        description="Plain password (will be hashed server-side)"
    )
    role: UserRole = Field(
        title="User Role",
        description="system role assigned to the user",
        json_schema_extra={
            "examples": ["ADMIN", "AGENT"]
        }
                       )
    
    user_code: Optional[UserCodeStr] = None

    @model_validator(mode="after")
    def validate_user_code(self):
        if self.role == UserRole.ADMIN:
            self.user_code = "KVR"

        elif self.role == UserRole.TEST_USER:
            self.user_code = "TST"

        elif self.role == UserRole.AGENT:
            if self.user_code is None:
                raise ValueError("user_code is required for AGENT role")
        
            self.user_code = self.user_code.upper()

        return self


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    public_id: str

    name: str
    phone: str
    role: UserRole
    is_active: bool
    user_code: UserCodeStr
    villages: list[VillageRead] = Field(default_factory=list)   # Villages assigned to an Agent
    last_login_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: Optional[NonEmptyStr] = Field(
        default=None
        )
    phone: Optional[PhoneStr] = Field(
        default=None
        )

    is_active: Optional[bool] = Field(
        default=None
        )
    
    user_code: Optional[UserCodeStr] = Field(
        default=None
    )



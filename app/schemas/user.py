from pydantic import BaseModel, Field, StringConstraints, model_validator
from typing import Optional, Annotated
from datetime import datetime

from app.models.core_models.user import UserRole
from app.schemas.village import VillageRead

StrongPassword = Annotated[
    str,
    StringConstraints(
        min_length=8
    )
]

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
                    min_length=10,
                    max_length=10,
                    pattern=r"^\d{10}$"
                    )
                ]

UserCodeStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^[A-Z0-9]{3}$"
    )
]

RESERVED_USER_CODES = {"KVR", "TST"}


class UserCreate(BaseModel):
    name: NonEmptyStr = Field(
        title="User Name",
        description="Display name of the User"
                       )
    phone: PhoneStr = Field(
        description="Phone number of the user"
    )
    password: StrongPassword = Field(
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
    def validate_user(self):
        # --- user_code validation ---
        if self.role == UserRole.ADMIN:
            if self.user_code and self.user_code != "KVR":
                raise ValueError("ADMIN user_code must be 'KVR'")
            self.user_code = "KVR"

        elif self.role == UserRole.TEST_USER:
            if self.user_code and self.user_code != "TST":
                raise ValueError("TEST_USER user_code must be 'TST'")
            self.user_code = "TST"

        elif self.role == UserRole.AGENT:
            if not self.user_code:
                raise ValueError("user_code is required for AGENT role")
            
            code = self.user_code.upper()
            
            if code in RESERVED_USER_CODES:
                raise ValueError("user_code is reserved and cannot be used for AGENT")

            self.user_code = code

        # --- password validation ---
        v = self.password

        if (
            not any(c.islower() for c in v) or
            not any(c.isupper() for c in v) or
            not any(c.isdigit() for c in v) or
            not any(not c.isalnum() for c in v)
        ):
            raise ValueError(
                "Password must include lowercase, uppercase, digit, and special character"
            )

        return self 


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    public_id: str

    name: str
    phone: str
    role: UserRole
    is_active: bool
    user_code: UserCodeStr  # since we fetch from db where the field is non null setting it optional here is incorrect
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
    @model_validator(mode="after")
    def validate_user_code_update(self):
        if self.user_code is not None:
            if not self.user_code:  
                raise ValueError("user_code cannot be empty")

            code = self.user_code.upper()

            if code in RESERVED_USER_CODES:
                raise ValueError("user_code is reserved")
            
            self.user_code = code

        return self



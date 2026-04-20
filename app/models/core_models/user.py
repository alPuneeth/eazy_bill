# standard library
from typing import Optional
from enum import Enum
from datetime import datetime

# third-party
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Enum as SAEnum, Column, String

# local module
from app.models.utilities import TimestampMixin, generate_uuid
# from app.models.lookup.village import Village
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lookup.village import Village


class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    TEST_USER = "test_user"


class User(TimestampMixin, SQLModel, table=True):
    """
    User represents an authenticated system actor.

    This model stores identity, authentication, and authorization-related
    information for users who can access the system. Role-based access
    control is enforced via a constrained enum stored at the database level.

    The model defines persistence and integrity only.
    Authentication rules, password policies, and authorization logic
    are enforced at the application or service layer.

    """
    id: Optional[int] = Field(
        default=None,
        primary_key=True
        )

    public_id: str = Field(
        ...,
        nullable=False,
        default_factory=generate_uuid,
        unique=True)

    name: str = Field(
        ...,
        nullable=False,
        max_length=150
        )

    phone: str = Field(
        ...,
        nullable=False,
        unique=True,
        max_length=15
        )

    hashed_password: str = Field(
        ...,
        nullable=False
        )

    # role is unique - only one admin and multiple staff are allowed
    role: UserRole = Field(
        ...,
        sa_column=Column(
            SAEnum(UserRole,
                   name="userrole",
                   native_enum=True,
                   values_callable=lambda enum: [e.value for e in enum] 
                   ),
            unique=False,
            nullable=False)
            )

    is_active: bool = Field(
        default=True,
        nullable=False
        )
    
    user_code: str = Field(
        ...,
        max_length=3,
        sa_column=Column(
            String(3),
            nullable=False,
            unique=True
    ))

    # Timestamp of the user's last successful login
    # remember to manually refresh before committing to DB
    last_login_at: Optional[datetime] = Field(
        default=None,
        nullable=True
        )

    villages: list["Village"]=Relationship(back_populates="agent")

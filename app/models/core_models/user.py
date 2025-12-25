# standard library
from typing import Optional
from enum import Enum
from datetime import datetime

# third-party
from sqlmodel import SQLModel, Field
from sqlalchemy import Enum as SAEnum, Column

# local module
from app.models.utilities import TimestampMixin, generate_uuid


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
        max_length=50,
        unique=True
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


    # role is unique - only one fgftradmin and only one staff are allowed
    role: UserRole = Field(
        ...,
        sa_column=Column(
            SAEnum(UserRole),
            unique=True)
            )

    is_active: bool = Field(
        default=True,
        nullable=False
        )

    # Timestamp of the user's last successful login
    # remember to manually refresh before committing to DB
    last_login_at: Optional[datetime] = Field(
        default=None,
        nullable=True
        )

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
    id: Optional[int] = Field(default=None, primary_key=True)
    public_id: str = Field(default_factory=generate_uuid, unique=True)
    name: str = Field(index=True, unique=True)  # check if this is OK
    phone: str = Field(unique=True)
    hashed_password: str

    # role is unique - only one admin and only one staff are allowed
    role: UserRole = Field(sa_column=Column(SAEnum(UserRole), unique=True))
    is_active: bool = Field(default=True, nullable=False)

    # remember to manually refresh before committing to DB
    last_login_at: Optional[datetime] = Field(default=None)

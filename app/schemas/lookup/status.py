from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.lookup.status import StatusEnum


class StatusCreate(BaseModel):
    name: StatusEnum = Field(
        title="Status",
        description="Operational state of the entity",
        json_schema_extra={
            "examples": ["active", "inactive", "archived"]
            }
        )
    description: Optional[str] = Field(default=None)


class StatusRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: StatusEnum
    description: Optional[str] = Field(default=None)
    created_at: datetime
    updated_at: datetime


class StatusUpdate(BaseModel):
    name: Optional[StatusEnum] = Field(default=None)
    description: Optional[str] = Field(default=None)

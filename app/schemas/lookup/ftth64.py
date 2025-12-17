from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FTTH64Create(BaseModel):
    name: str = Field(
        title="FTTH64",
        description="Identifier representing an FTTH 64-port"
        "configuration type used for network provisioning."
    )

    code: str

    description: Optional[str] = Field(default=None)


class FTTH64Read(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    code: str
    description: Optional[str] = Field(default=None)

    created_at: datetime
    updated_at: datetime


class FTTH64Update(BaseModel):
    name: Optional[str] = Field(default=None)
    code: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

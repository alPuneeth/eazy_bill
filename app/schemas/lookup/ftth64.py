from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

NameStr = Annotated[
    str,
    StringConstraints(
        min_length=1,
        to_lower=True,
        strip_whitespace=True,
        max_length=100
    )]


class FTTH64Create(BaseModel):
    name: NameStr = Field(
        title="FTTH64",
        description="Identifier representing an FTTH 64-port"
        "configuration type used for network provisioning."
    )

    description: Optional[str] = Field(
        default=None
        )


class FTTH64Read(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: Optional[str] = Field(default=None)

    created_at: datetime
    updated_at: datetime


class FTTH64Update(BaseModel):
    name: Optional[NameStr] = Field(default=None
                                        )
    description: Optional[str] = Field(default=None
                                       )

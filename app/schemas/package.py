from pydantic import BaseModel, StringConstraints, Field
from typing import Optional, Annotated
from datetime import datetime

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]

DesStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]


class PackageCreate(BaseModel):
    name: NameStr = Field(
        title="Package",
        description="Name of the Package"
    )
    price: float = Field(
        gt=0,
        title="Price",
        description="Price of the Package"
    )
    description: Optional[str] = Field(default=None)


class PackageRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    price: float
    description: Optional[str]

    created_at: datetime
    updated_at: datetime


class PackageUpdate(BaseModel):
    name: Optional[NameStr] = Field(
        default=None
        )
    price: Optional[float] = Field(
        default=None, gt=0
        )
    description: Optional[str] = Field(
        default=None
        )


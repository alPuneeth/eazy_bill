from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime


VillageNameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]

PostalCodeStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=6,
        pattern="^[1-9][0-9]{5}$"
    )
]

VillageCodeStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]


class ReplaceVillagesRequest(BaseModel):
    village_ids: list[int]


class AssignVillagesRequest(BaseModel):
    village_ids: list[int]
    force: bool = False


class VillageCreate(BaseModel):
    name: VillageNameStr = Field(
        title="Village Name",
        description="Name of the village"
    )
    postal_code: PostalCodeStr = Field(
        title="Postal code",
        description="Displays postal code of the village"
    )
    village_code: VillageCodeStr


class VillageRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    postal_code: str
    village_code: str
    agent_public_id: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class VillageUpdate(BaseModel):
    name: Optional[VillageNameStr] = Field(
        default=None
        )
    postal_code: Optional[PostalCodeStr] = Field(
        default=None
        )
    village_code: Optional[VillageCodeStr] = Field(
        default=None
        )


class AssignVillagesResponse(BaseModel):
    assigned: list[VillageRead]
    already_assigned: list[int]

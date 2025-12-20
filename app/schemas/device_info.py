from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Optional
from datetime import datetime


AccountNumberStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=30
    )
]

VCStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=30
    )
]


class DeviceInfoCreate(BaseModel):
    account_number: AccountNumberStr = Field(
        title="Account Number",
    )
    stb_id: int = Field(
        title="STB id",
        description="Set Top Box id"
    )
    vc_number: VCStr = Field(
        title="VC number",
        description="Viewing Card number"
    )
    previous_vc_number: Optional[VCStr] = Field(
        default=None,
        title="Previous vc number",
        description="Previous Viewing Card number"
    )

    customer_id: int
    tvtype_id: int
    status_id: int


class DeviceInfoRead(BaseModel):
    model_config = {"from_attributes": True}

    public_id: str
    account_number: str
    stb_id: int
    vc_number: str
    previous_vc_number: Optional[str]

    customer_id: int
    tvtype_id: int
    status_id: int

    created_at: datetime
    updated_at: datetime


class DeviceInfoUpdate(BaseModel):
    account_number: Optional[AccountNumberStr] = Field(
        default=None
        )
    stb_id: Optional[int] = Field(
        default=None
        )
    vc_number:  Optional[VCStr] = Field(
        default=None
        )
    previous_vc_number:  Optional[VCStr] = Field(
        default=None
        )

    customer_id:  Optional[int] = Field(
        default=None
        )
    tvtype_id:  Optional[int] = Field(
        default=None
        )
    status_id:  Optional[int] = Field(
        default=None
        )

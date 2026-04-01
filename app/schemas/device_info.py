from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated, Optional
from datetime import datetime

from app.schemas.common import IdValueRead


AccountNumberStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]

VCStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]


class DeviceInfoCreate(BaseModel):
    account_number: Optional[AccountNumberStr] = Field(
        default=None,
        title="Account Number",
    )
    stb_id: Optional[str] = Field(
        default=None,
        title="STB id",
        description="Set Top Box id"
    )
    vc_number: VCStr = Field(
        ...,
        title="VC number",
        description="Viewing Card number"
    )
    previous_vc_number: Optional[VCStr] = Field(
        default=None,
        title="Previous vc number",
        description="Previous Viewing Card number"
    )
    tv_name: Optional[NameStr] = Field(
        default=None,
        title="TV name",
        description="Brand or manufacturer name of the TV"
    )

    customer_public_id: str  # changed from customer_id: int

    tvtype_id: Optional[int] = Field(
        default=None,
        title="TV Type"
    )

    status_id: int


class DeviceInfoRead(BaseModel):
    model_config = {"from_attributes": True}

    public_id: str
    account_number: Optional[str] = None
    stb_id: Optional[str] = None
    vc_number: str
    previous_vc_number: Optional[str] = None
    tv_name: Optional[str] = None

    customer_public_id: str  # changed from customer_id: int

    tvtype: Optional[IdValueRead] = None # changed from int to IdValueRead --> Read models expose meaning, not IDs
    status: IdValueRead

    created_at: datetime
    updated_at: datetime


class DeviceInfoUpdate(BaseModel):
    account_number: Optional[AccountNumberStr] = Field(
        default=None
        )
    stb_id: Optional[str] = Field(
        default=None
        )
    vc_number:  Optional[VCStr] = Field(
        default=None
        )
    previous_vc_number:  Optional[VCStr] = Field(
        default=None
        )
    tv_name:  Optional[NameStr] = Field(
        default=None
        )
    tvtype_id:  Optional[int] = Field(
        default=None
        )
    status_id:  Optional[int] = Field(
        default=None
        )

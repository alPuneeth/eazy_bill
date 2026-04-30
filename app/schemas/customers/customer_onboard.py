from decimal import Decimal

from pydantic import (BaseModel, Field, StringConstraints,
                      field_validator, PydanticUserError
                      )
from typing import Optional, Annotated
from datetime import datetime

from app.schemas.common import IdValueRead, VillageSummary
from app.schemas.bill import BillRead

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=150
    )
]

CodeStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=100
    )
]

PhoneStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=10
    )
]

AadhaarStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=12,
        pattern="^[2-9]\\d{11}$"
    )
]

AccountNumberStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True,
                      max_length=100
                      )
]

VCStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True,
                      max_length=100
                      )
]

TVNameStr = Annotated[
    str,
    StringConstraints(strip_whitespace=True,
                      min_length=1,
                      max_length=100
                      )
]


class CustomerOnboardCreate(BaseModel):
    """
    Composite request model for customer onboarding screen.
    Matches UI exactly. Used only for orchestration.
    """
    name: NameStr = Field(
        title="Customer Name",
        description="Displays customer name"
        )

    phone: PhoneStr = Field(
        title="Mobile number",
        description="Displays customer's phone number"
        )

    alternate_number: Optional[PhoneStr] = Field(
        default=None
        )

    aadhaar_number: Optional[AadhaarStr] = Field(
        default=None,
        title="Aadhaar Number",
        description="Displays Aadhaar number"
        )

    @field_validator("aadhaar_number", mode="before")
    @classmethod
    def validate_aadhaar(cls, v):
        if v is None:
            return v
        if not v.isdigit() or len(v) != 12 or v[0] in {"0", "1"}:
            raise ValueError("Please enter a valid 12-digit Aadhaar number")
        return v

    upi_id: Optional[str] = Field(
        default=None,
        title="UPI ID",
        description="Displays upi id of the customer"
        )

    village_id: int = Field(
        title="Village",
        description="Village the customer belongs to"
    )

    customer_type_id: int = Field(
        title="Customer Type",
        description="Classification of the customer"
    )

    ftth8_code: Optional[CodeStr] = Field(
        default=None,
        title="FTTH64 code of the Customer"
    )

    ftth64_id: int = Field(
        title="FTTH64 id"
        )

    package_id: int = Field(
        title="Package id"
    )

    description: Optional[str] = Field(
        default=None
        )
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

    # new field in DeviceInfo
    tv_name: Optional[TVNameStr] = Field(
        default=None,
        title="TV name"
    )
    tvtype_id: Optional[int] = Field(
        default=None,
        title="TVType"
        )


class CustomerListRead(BaseModel):
    model_config = {
        "from_attributes": True,
        "json_encoders": {Decimal: float}
        }

    public_id: str
    name: str
    phone: str
    vc_number: str
    status: str
    monthly_rate: Decimal = Field(max_digits=10, decimal_places=2)
    expiry_date: Optional[datetime]
    village: str


class CustomerOnboardRead(BaseModel):
    model_config = {
        "from_attributes": True,
        "json_encoders": {Decimal: float}
        }
    # ---------- Customer ----------
    public_id: str
    name: str
    phone: str
    alternate_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    upi_id: Optional[str] = None
    ftth8_code: Optional[str] = None

    village: VillageSummary
    customer_type: IdValueRead
    ftth64: Optional[IdValueRead] = None

    description: Optional[str] = None

    # ---------- Device ----------
    account_number: Optional[str] = None
    stb_id: Optional[str] = None
    vc_number: str
    previous_vc_number: Optional[str] = None
    tv_name: Optional[str] = None

    tvtype: Optional[IdValueRead] = None
    status: IdValueRead

    # ---------- CurrentPackage ----------
    package: IdValueRead
    monthly_rate: Decimal = Field(max_digits=10, decimal_places=2)

    # ---------- Latest Bill (FULL OBJECT) ----------
    latest_bill: Optional[BillRead] = None

    # ---------- Meta ----------
    created_at: datetime
    updated_at: datetime


class CustomerOnboardUpdate(BaseModel):
    # ---- Customer ----
    name: Optional[NameStr] = None
    phone: Optional[PhoneStr] = None
    alternate_number: Optional[PhoneStr] = None
    aadhaar_number: Optional[AadhaarStr] = None

    @field_validator("aadhaar_number")
    @classmethod
    def validate_aadhaar(cls, v):
        if v is None:
            return v
        if not v.isdigit() or len(v) != 12 or v[0] in {"0", "1"}:
            raise ValueError("Please enter a valid 12-digit Aadhaar number")
        return v

    upi_id: Optional[str] = None
    village_id: Optional[int] = None
    customer_type_id: Optional[int] = None
    ftth8_code: Optional[CodeStr] = None
    ftth64_id: Optional[int] = None
    package_id: Optional[int] = None
    description: Optional[str] = None

    # ---- Device ----
    account_number: Optional[AccountNumberStr] = None
    stb_id: Optional[str] = None
    vc_number: Optional[VCStr] = None
    previous_vc_number: Optional[VCStr] = None
    tv_name: Optional[str] = None
    tvtype_id: Optional[int] = None


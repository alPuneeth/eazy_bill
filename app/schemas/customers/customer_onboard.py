from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

from app.schemas.common import IdValueRead
from app.schemas.bill import BillRead

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=150
    )
]

PhoneStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=15
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

    ftth64_id: int = Field(
        title="FTTH64 id"
        )

    package_id: int = Field(
        title="Package id"
    )

    description: Optional[str] = Field(
        default=None
        )
    account_number: AccountNumberStr = Field(
        title="Account Number",
    )
    stb_id: str = Field(
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

    # new field in DeviceInfo
    tv_name: Optional[TVNameStr] = Field(
        default=None,
        title="TV name"
    )
    tvtype_id: int = Field(
        title="TVType"
        )
    status_id: int = Field(
        title="Status"
        )


class CustomerListRead(BaseModel):
    model_config = {
        "from_attributes": True
        }

    public_id: str
    name: str
    phone: str
    vc_number: str
    status: str
    monthly_rate: int
    expiry_date: Optional[datetime]
    village: str


class CustomerOnboardRead(BaseModel):
    model_config = {
        "from_attributes": True
        }
    # ---------- Customer ----------
    public_id: str
    name: str
    phone: str
    alternate_number: Optional[str]
    aadhaar_number: Optional[str]
    upi_id: Optional[str]

    village: IdValueRead
    customer_type: IdValueRead
    ftth64: IdValueRead

    description: Optional[str]

    # ---------- Device ----------
    account_number: str
    stb_id: str
    vc_number: str
    previous_vc_number: Optional[str]
    tv_name: Optional[NameStr]

    tvtype: IdValueRead
    status: IdValueRead

    # ---------- CurrentPackage ----------
    package: IdValueRead
    monthly_rate: float

    # ---------- Latest Bill (FULL OBJECT) ----------
    latest_bill: Optional[BillRead] = None

    # ---------- Meta ----------
    created_at: datetime
    updated_at: datetime


class CustomerOnboardUpdate(BaseModel):
    # ---- Customer ----
    name: Optional[str] = None
    phone: Optional[str] = None
    alternate_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    upi_id: Optional[str] = None
    village_id: Optional[int] = None
    customer_type_id: Optional[int] = None
    ftth64_id: Optional[int] = None
    package_id: Optional[int] = None
    description: Optional[str] = None

    # ---- Device ----
    account_number: Optional[str] = None
    stb_id: Optional[str] = None
    vc_number: Optional[str] = None
    previous_vc_number: Optional[str] = None
    tv_name: Optional[str] = None
    tvtype_id: Optional[int] = None
    status_id: Optional[int] = None
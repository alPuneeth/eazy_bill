from pydantic import BaseModel, Field, StringConstraints
from typing import Optional, Annotated
from datetime import datetime

from app.schemas.common import IdValueRead

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
        min_length=12,
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


class CustomerCreate(BaseModel):

    name: NameStr = Field(
        title="Name",
        description="Displays customer name"
        )

    phone: PhoneStr = Field(
        title="Phone number",
        description="Displays customer's phone number"
        )

    alternate_number: Optional[PhoneStr] = Field(
        default=None
        )

    aadhaar_number: Optional[AadhaarStr] = Field(
        default=None,
        title="Aadhaar number",
        description="Displays aadhaar number"
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


class CustomerRead(BaseModel):
    model_config = {"from_attributes": True}

    public_id: str

    name: str
    phone: str
    alternate_number: Optional[str]
    upi_id: Optional[str]

    village: IdValueRead
    customer_type: IdValueRead
    ftth64: IdValueRead
    package: IdValueRead

    created_at: datetime
    updated_at: datetime
    description: Optional[str]


class CustomerUpdate(BaseModel):

    name: Optional[NameStr] = Field(
        default=None
        )
    phone: Optional[PhoneStr] = Field(
        default=None
        )
    alternate_number: Optional[PhoneStr] = Field(
        default=None
        )
    aadhaar_number: Optional[AadhaarStr] = Field(
        default=None
        )
    upi_id: Optional[str] = Field(
        default=None
        )

    village_id: Optional[int] = Field(
        default=None
        )
    ftth64_id: Optional[int] = Field(
        default=None
        )
    customer_type_id: Optional[int] = Field(
        default=None
        )
    package_id: Optional[int] = Field(
        default=None
    )
    description: Optional[str] = Field(
        default=None
        )
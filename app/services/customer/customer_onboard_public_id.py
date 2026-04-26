# single payload - response model for a customer
from sqlmodel import Session
from fastapi import HTTPException
from sqlalchemy import select

from app.services.customer.enforce_customer_vis import enforce_customer_visibility
from app.schemas.customers.customer_onboard import (
    CustomerOnboardRead, CustomerOnboardUpdate
    )
from app.schemas.common import IdValueRead, VillageSummary, CreatorSummary

from app.models.core_models.customer import Customer
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.village import Village
from app.models.lookup.customer_type import CustomerType
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.tv_type import TVType
from app.models.lookup.status import Status, StatusEnum
from app.models.lookup.package import Package
from app.models.bill.bill import Bill
from app.schemas.bill import BillRead
from app.models.core_models.user import User 
from app.services.customer.get_cus_by_public_id import get_customer_by_public_id


def build_customer_onboard_read(customer_public_id: str, session: Session, current_user: User):
    """
    Optimized single-customer onboard read.

    - Explicit joins for customer core data
    - Separate, clear latest-bill fetch
    - Correct ORM → schema mapping
    """

    # -------- Fetch customer + core joins --------
    stmt = (
        select(
            Customer,
            Village,
            CustomerType,
            FTTH64,
            Package,
            DeviceInfo,
            TVType,
            Status,
        )
        .join(Village, Village.id == Customer.village_id)
        .join(CustomerType, CustomerType.id == Customer.customer_type_id)
        .join(FTTH64, FTTH64.id == Customer.ftth64_id)
        .join(Package, Package.id == Customer.package_id)
        .join(DeviceInfo, DeviceInfo.customer_id == Customer.id)
        .outerjoin(TVType, TVType.id == DeviceInfo.tvtype_id)
        .join(Status, Status.id == DeviceInfo.status_id)
        .where(Customer.public_id == customer_public_id)
    )

    row = session.exec(stmt).first()

    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")

    (
        customer,
        village,
        customer_type,
        ftth64,
        package_,
        device,
        tvtype,
        status,
    ) = row

    enforce_customer_visibility(customer, current_user, session)

    # -------- Fetch latest bill (explicit & safe) --------
    bill_row = session.execute(
        select(Bill, Package, User)
        .join(Package, Package.id == Bill.package_id)
        .join(User, User.id == Bill.created_by_id)
        .where(Bill.customer_id == customer.id)
        .order_by(Bill.created_at.desc())
        .limit(1)
    ).first()

    latest_bill_read = None
    if bill_row:
        bill, bill_package, creator = bill_row
        latest_bill_read = BillRead(
            public_id=bill.public_id,
            bill_code=bill.bill_code,
            bill_date=bill.bill_date,
            start_date=bill.start_date,
            end_date=bill.end_date,
            monthly_count=bill.monthly_count,
            bill_amount=bill.bill_amount,

            customer_public_id=customer.public_id,

            package_id=IdValueRead(
                id=bill_package.id,
                value=bill_package.name
            ),
            created_by_id=CreatorSummary(
                id=creator.id,
                public_id=creator.public_id,
                name=creator.name
            ),

            created_at=bill.created_at,
            updated_at=bill.updated_at,
        )

    # -------- Assemble response --------
    return CustomerOnboardRead(
        public_id=customer.public_id,
        name=customer.name,
        phone=customer.phone,
        alternate_number=customer.alternate_number,
        aadhaar_number=customer.aadhaar_number,
        upi_id=customer.upi_id,

        village=VillageSummary(id=village.id, name=village.name, village_code=village.village_code),
        customer_type=IdValueRead(id=customer_type.id, value=customer_type.name),
        ftth64=IdValueRead(id=ftth64.id, value=ftth64.name),

        description=customer.description,

        account_number=device.account_number,
        stb_id=device.stb_id,
        vc_number=device.vc_number,
        previous_vc_number=device.previous_vc_number,
        tv_name=device.tv_name,

        tvtype=IdValueRead(id=tvtype.id, value=tvtype.name) if tvtype else None,
        status=IdValueRead(id=status.id, value=status.name),
        ftth8_code=customer.ftth8_code,

        package=IdValueRead(id=package_.id, value=package_.name),
        monthly_rate=package_.price,

        latest_bill=latest_bill_read,

        created_at=customer.created_at,
        updated_at=customer.updated_at
    )


def patch_customer_onboard(
    customer_public_id: str,
    payload: CustomerOnboardUpdate,
    session: Session,
    current_user: User
):
    # Fetch customer
    customer = get_customer_by_public_id(session, customer_public_id)
   
    enforce_customer_visibility(customer, current_user, session)

    # Fetch device (single active device assumption)
    device = session.exec(
        select(DeviceInfo).where(DeviceInfo.customer_id == customer.id)
    ).scalars().first()

    if not device:
        raise ValueError("Device not found")

    data = payload.model_dump(exclude_unset=True)

    # ---- status control ----
    if "status_id" in data:
        new_status = session.get(Status, data["status_id"])
        if not new_status:
            raise ValueError("Invalid status")

        current_status = session.get(Status, device.status_id)

        # Only allow ARCHIVED or restore from ARCHIVED
        if new_status.name == StatusEnum.ARCHIVED:
            pass  # allowed (opt-out)

        elif current_status.name == StatusEnum.ARCHIVED and new_status.name == StatusEnum.INACTIVE:
            pass  # allowed restore

        else:
            raise ValueError("Customer cannot be activated without a valid bill")

    if "tvtype_id" in data and data["tvtype_id"] is not None:
        tvtype = session.get(TVType, data["tvtype_id"])
        if not tvtype:
            raise ValueError("Invalid TV type")

    # ---- Split payload ----
    customer_fields = {
        k: v for k, v in data.items()
        if k in {
            "name", "phone", "alternate_number", "aadhaar_number",
            "upi_id", "village_id", "customer_type_id", "ftth8_code",
            "ftth64_id", "package_id", "description"
        }
    }

    device_fields = {
        k: v for k, v in data.items()
        if k in {
            "account_number", "stb_id", "vc_number",
            "previous_vc_number", "tv_name",
            "tvtype_id", "status_id"
        }
    }

    # ---- Apply updates ----
    for k, v in customer_fields.items():
        setattr(customer, k, v)

    for k, v in device_fields.items():
        setattr(device, k, v)

    return customer

# TODO (security): enforce customer visibility in GET/PATCH/POST
# once feature development stabilizes

# single payload - response model for a customer
from sqlmodel import Session
from fastapi import HTTPException
from sqlalchemy import select

from app.schemas.customers.customer_onboard import (
    CustomerOnboardRead, CustomerOnboardUpdate
    )
from app.schemas.common import IdValueRead

from app.models.core_models.customer import Customer
from app.models.devices.device_info import DeviceInfo
from app.models.lookup.village import Village
from app.models.lookup.customer_type import CustomerType
from app.models.lookup.ftth64 import FTTH64
from app.models.lookup.tv_type import TVType
from app.models.lookup.status import Status
from app.models.lookup.package import Package
from app.models.bill.bill import Bill
from app.schemas.bill import BillRead
from app.models.core_models.user import User 



def build_customer_onboard_read(customer_public_id: str, session: Session):
    # """
    # Optimized onboard read:
    # • Single DB round-trip
    # • sqlmodel.select + add_columns
    # • Explicit joins
    # • session.exec (SQLModel-preferred)
    # • Minimal, explicit typing escape hatch
    # """

    # stmt = (
    #     select(
    #         Customer,
    #         Village,
    #         CustomerType,
    #         FTTH64,
    #         Package,
    #         DeviceInfo,
    #         TVType,
    #         Status,
    #     )
    #     .select_from(Customer)
    #     .join(Village, Village.id == Customer.village_id)
    #     .join(CustomerType, CustomerType.id == Customer.customer_type_id)
    #     .join(FTTH64, FTTH64.id == Customer.ftth64_id)
    #     .join(Package, Package.id == Customer.package_id)
    #     .join(DeviceInfo, DeviceInfo.customer_id == Customer.id)
    #     .join(TVType, TVType.id == DeviceInfo.tvtype_id)
    #     .join(Status, Status.id == DeviceInfo.status_id)
    #     .where(Customer.public_id == customer_public_id)
    # )

    # result = session.execute(stmt).first()

    # if not result:
    #     raise HTTPException(
    #         status_code=404,
    #         detail="Customer not found"
    #     )

    # (
    #     customer,
    #     village,
    #     customer_type,
    #     ftth64,
    #     package_,
    #     device,
    #     tvtype,
    #     status,
    # ) = result

    # # -------- Fetch latest bill (explicit & safe) --------
    # latest_bill = session.execute(
    #     select(Bill)
    #     .where(Bill.customer_id == customer.id)
    #     .order_by(Bill.created_at.desc())
    #     .limit(1)
    #     ).scalars().one_or_none()

    # return CustomerOnboardRead(
    #     public_id=customer.public_id,
    #     name=customer.name,
    #     phone=customer.phone,
    #     alternate_number=customer.alternate_number,
    #     aadhaar_number=customer.aadhaar_number,
    #     upi_id=customer.upi_id,

    #     village=IdValueRead(id=village.id, value=village.name),
    #     customer_type=IdValueRead(id=customer_type.id,
    #                               value=customer_type.name),
    #     ftth64=IdValueRead(id=ftth64.id, value=ftth64.name),

    #     description=customer.description,

    #     account_number=device.account_number,
    #     stb_id=device.stb_id,
    #     vc_number=device.vc_number,
    #     previous_vc_number=device.previous_vc_number,
    #     tv_name=device.tv_name,

    #     tvtype=IdValueRead(id=tvtype.id, value=tvtype.name),
    #     status=IdValueRead(id=status.id, value=status.name),

    #     package=IdValueRead(id=package_.id, value=package_.name),
    #     monthly_rate=package_.price,

    #     latest_bill = latest_bill,

    #     created_at=customer.created_at,
    #     updated_at=customer.updated_at,
    # )
    # def build_customer_onboard_read(customer_public_id: str, session: Session) -> CustomerOnboardRead:
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
        .join(TVType, TVType.id == DeviceInfo.tvtype_id)
        .join(Status, Status.id == DeviceInfo.status_id)
        .where(Customer.public_id == customer_public_id)
    )

    row = session.execute(stmt).first()

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
            created_by_id=IdValueRead(
                id=creator.id,
                value=creator.name
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

        village=IdValueRead(id=village.id, value=village.name),
        customer_type=IdValueRead(id=customer_type.id, value=customer_type.name),
        ftth64=IdValueRead(id=ftth64.id, value=ftth64.name),

        description=customer.description,

        account_number=device.account_number,
        stb_id=device.stb_id,
        vc_number=device.vc_number,
        previous_vc_number=device.previous_vc_number,
        tv_name=device.tv_name,

        tvtype=IdValueRead(id=tvtype.id, value=tvtype.name),
        status=IdValueRead(id=status.id, value=status.name),
        ftth64_code=customer.ftth64_code,

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
):
    # Fetch customer
    customer = session.execute(
        select(Customer).where((Customer.public_id == customer_public_id))
    ).scalars().first()

    if not customer:
        raise ValueError("Customer not found")

    # Fetch device (single active device assumption)
    device = session.execute(
        select(DeviceInfo).where(DeviceInfo.customer_id == customer.id)
    ).scalars().first()

    if not device:
        raise ValueError("Device not found")

    data = payload.model_dump(exclude_unset=True)

    # ---- Split payload ----
    customer_fields = {
        k: v for k, v in data.items()
        if k in {
            "name", "phone", "alternate_number", "aadhaar_number",
            "upi_id", "village_id", "customer_type_id", "ftth64_code",
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

    session.commit()
    session.refresh(customer)

    return customer.public_id

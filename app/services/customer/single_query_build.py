from sqlmodel import Session
from sqlalchemy import select, func, and_

from app.schemas.customers.customer_onboard import CustomerOnboardRead
from app.schemas.common import IdValueRead, VillageSummary

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


def build_customer_onboard_list(session: Session) -> list[CustomerOnboardRead]:
    """
    Single-query, full customer read for list endpoints.

    - ONE SQL query
    - OUTER JOINs only
    - Safe for dirty data
    - No N+1 queries
    """

    # ---- subquery to determine latest bill per customer ----
    latest_bill_sq = (
        select(
            Bill.customer_id,
            func.max(Bill.bill_date).label("max_bill_date")
    )
    .group_by(Bill.customer_id)
    .subquery()
    )

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
            Bill,
            User
        )
        .outerjoin(Village, Village.id == Customer.village_id)
        .outerjoin(CustomerType, CustomerType.id == Customer.customer_type_id)
        .outerjoin(FTTH64, FTTH64.id == Customer.ftth64_id)
        .outerjoin(Package, Package.id == Customer.package_id)
        .outerjoin(DeviceInfo, DeviceInfo.customer_id == Customer.id)
        .outerjoin(TVType, TVType.id == DeviceInfo.tvtype_id)
        .outerjoin(Status, Status.id == DeviceInfo.status_id)
        .outerjoin(
            latest_bill_sq,
            latest_bill_sq.c.customer_id == Customer.id
                   )
        .outerjoin(
                Bill,
                and_(
                       Bill.customer_id == Customer.id,
                       Bill.bill_date == latest_bill_sq.c.max_bill_date
                   )
                   )
        .outerjoin(User, User.id == Bill.created_by_id)
        .order_by(Customer.created_at.desc())
    )

    rows = session.execute(stmt).all()

    results: list[CustomerOnboardRead] = []

    for (
        customer,
        village,
        customer_type,
        ftth64,
        package_,
        device,
        tvtype,
        status,
        bill,
        creator
    ) in rows:

        latest_bill = None
        if bill:
            latest_bill = BillRead(
                                public_id=bill.public_id,
                                bill_code=bill.bill_code,
                                bill_date=bill.bill_date,
                                start_date=bill.start_date,
                                end_date=bill.end_date,
                                monthly_count=bill.monthly_count,
                                bill_amount=bill.bill_amount,

                                customer_public_id=customer.public_id,

                                package_id=(
                                    IdValueRead(id=package_.id, value=package_.name)
                                    if package_ else None
                                ),
                                created_by_id=(
                                    IdValueRead(id=creator.id, value=creator.name)
                                    if creator else None
                                ),

                                created_at=bill.created_at,
                                updated_at=bill.updated_at,
                            )

        results.append(
            CustomerOnboardRead(
                public_id=customer.public_id,
                name=customer.name,
                phone=customer.phone,
                alternate_number=customer.alternate_number,
                aadhaar_number=customer.aadhaar_number,
                upi_id=customer.upi_id,

                village=(
                    VillageSummary(id=village.id, name=village.name, village_code=village.village_code)
                    if village else None
                ),
                customer_type=(
                    IdValueRead(id=customer_type.id, value=customer_type.name)
                    if customer_type else None
                ),

                ftth64_code=customer.ftth64_code,

                ftth64=(
                    IdValueRead(id=ftth64.id, value=ftth64.name)
                    if ftth64 else None
                ),

                description=customer.description,

                account_number=device.account_number if device else None,
                stb_id=device.stb_id if device else None,
                vc_number=device.vc_number if device else None,
                previous_vc_number=device.previous_vc_number if device else None,
                tv_name=(
                        device.tv_name.strip()
                        if device and device.tv_name and device.tv_name.strip()
                        else None
                    ),

                tvtype=(
                    IdValueRead(id=tvtype.id, value=tvtype.name)
                    if tvtype else None
                ),
                status=(
                    IdValueRead(id=status.id, value=status.name)
                    if status else None
                ),

                package=(
                    IdValueRead(id=package_.id, value=package_.name)
                    if package_ else None
                ),
                monthly_rate=package_.price if package_ else None,

                latest_bill=latest_bill,

                created_at=customer.created_at,
                updated_at=customer.updated_at,
            )
        )

    return results

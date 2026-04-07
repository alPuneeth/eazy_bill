# used in (ACTIVE + INACTIVE) and ARCHIVED customers
from sqlmodel import select
from sqlalchemy import func

from app.models.core_models.customer import Customer
from app.models.lookup.village import Village
from app.models.lookup.package import Package
from app.models.bill.bill import Bill
from app.models.lookup.status import Status
from app.models.devices.device_info import DeviceInfo
from app.models.core_models.user import User


def build_customer_list_query(
        device_statuses: list[str],
        current_user: User):
    # Subquery: latest bill per customer
    latest_bill_subq = (
        select(
            Bill.customer_id,
            func.max(Bill.id).label("max_bill_id") 
        )
        .group_by(Bill.customer_id)
        .subquery()
    )

    stmt = (
        select(
            Customer.public_id,
            Customer.name,
            Customer.phone,
            DeviceInfo.vc_number,
            Status.name.label("status"),
            Village.name.label("village"),
            Bill.end_date.label("expiry_date"),
            Package.price.label("monthly_rate"),
        )
        # mandatory joins
        .join(DeviceInfo, DeviceInfo.customer_id == Customer.id)
        .join(Status, Status.id == DeviceInfo.status_id)
        .join(Village, Village.id == Customer.village_id)
        .join(Package, Package.id == Customer.package_id)

        # optional bill joins
        .outerjoin(
            latest_bill_subq,
            latest_bill_subq.c.customer_id == Customer.id,
        )
        .outerjoin(
            Bill,
            Bill.id == latest_bill_subq.c.max_bill_id
        )

        # device status filter
        .where(Status.name.in_(device_statuses))
    )

    # # 🔐 authorization rule - RBAC
    if current_user.role == "admin":
        pass
    else:
        stmt = stmt.where(Village.agent_id == current_user.id)

    return stmt

# used in (ACTIVE + INACTIVE) and ARCHIVED customers
from app.models.core_models.customer import Customer
from app.models.lookup.village import Village
from app.models.lookup.package import Package
from app.models.bill.bill import Bill
from app.models.lookup.status import Status
from app.models.devices.device_info import DeviceInfo
from sqlmodel import select
from sqlalchemy import and_
from sqlalchemy import func


def build_customer_list_query(device_statuses: list[str]):
      # Subquery: latest bill per customer
    latest_bill_subq = (
        select(
            Bill.customer_id,
            func.max(Bill.bill_date).label("latest_bill_date")
        )
        .group_by(Bill.customer_id)
        .subquery()
    )

    return (
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
        # joins
        .join(DeviceInfo, DeviceInfo.customer_id == Customer.id)
        .join(Status, Status.id == DeviceInfo.status_id)
        .join(Village, Village.id == Customer.village_id)
        .join(Package, Package.id == Customer.package_id)

        # join ONLY the latest bill
        .join(
            latest_bill_subq,
            latest_bill_subq.c.customer_id == Customer.id,
        )
        .join(
            Bill,
            and_(
                Bill.customer_id == latest_bill_subq.c.customer_id,
                Bill.bill_date == latest_bill_subq.c.latest_bill_date,
            ),
        )

        # filter by device status
        .where(Status.name.in_(device_statuses))
    )
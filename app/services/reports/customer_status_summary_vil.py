from sqlmodel import select, Session
from sqlalchemy import func, case

from app.schemas.reports.customer_status_summary_vil import (
    VillageCustomerStatusSummary
)
from app.models.core_models.customer import Customer
from app.models.core_models.user import User, UserRole
from app.models.lookup.village import Village
from app.models.lookup.status import Status
from app.models.devices.device_info import DeviceInfo


def get_customer_status_summary(
    *,
    session: Session,
    current_user: User
) -> list[VillageCustomerStatusSummary]:

    stmt = (
        select(
            Village.name.label("village_name"),

            func.sum(
                case(
                    (Status.name == "active", 1),
                    else_=0
                )
            ).label("active_count"),

            func.sum(
                case(
                    (Status.name == "inactive", 1),
                    else_=0
                )
            ).label("inactive_count"),

            func.count(Customer.id).label("total_count")
        )
        .select_from(Customer)
        .join(Village, Village.id == Customer.village_id)
        .join(DeviceInfo, DeviceInfo.customer_id == Customer.id)
        .join(Status, Status.id == DeviceInfo.status_id)
    )

    # RBAC FILTER — AGENT RESTRICTION
    if current_user.role == UserRole.AGENT:
        stmt = stmt.where(Village.agent_id == current_user.id)

    stmt = stmt.group_by(Village.name).order_by(Village.name)

    rows = session.exec(stmt).all()

    return [
        VillageCustomerStatusSummary(
            village_name=row.village_name,
            active_count=row.active_count,
            inactive_count=row.inactive_count,
            total_count=row.total_count
        )
        for row in rows
    ]
